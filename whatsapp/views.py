from django.shortcuts import render
from typing import List
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import WebhookObjectSerializer, WebhookMessageSerializer
from .models import SentMessages, ReceivedMessages, Webhook
from decouple import config
from zimgpt.tasks import process_whatsapp_state_input
from .aux_func import send_read_report
from .tasks import send_app_text
from zimgpt.models import Profile
import logging

logger = logging.getLogger(__name__)

verify_token = config('WA_WEBHOOK_VERIFY_TOKEN')
this_apps_number = config('WHATSAPP_NUMBER_ID')

# Create your views here.
class WebhookAPIView(generics.GenericAPIView):

    #receive and process the webhook
    def post(self, request):

        logger.debug("Received webhook data: %s", str(request.data))
        
        serializer = WebhookObjectSerializer(data=request.data)
        if serializer.is_valid():
            webhook = serializer.save()

            # check if we are responding
            # we only respond to messages from our phone
            if webhook.entry[0].changes[0].value.metadata.phone_number_id == this_apps_number:
                if webhook.entry[0].changes[0].value.messages:
                    self.on_message_received(request, webhook.entry[0].id, webhook.entry[0].changes[0].value.metadata, webhook.entry[0].changes[0].value.contacts, webhook.entry[0].changes[0].value.messages)
                elif webhook.entry[0].changes[0].value.statuses:
                    self.on_status_update(request, webhook.entry[0].id, webhook.entry[0].changes[0].value.metadata, webhook.entry[0].changes[0].value.statuses)

            return Response(None, status=status.HTTP_200_OK)
        else:
            #parsing failed
            logger.error("Serialising webhook Errors: %s; RequestData: %s", str(serializer.errors), str(request.data))
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        
    ## webhook events
    def on_message_received(self, request, account_id, metadata, contacts, messages: List[Webhook.Entry.Change.Value.Message]):
        logger.debug("Messages received")

        #index to iterate contacts
        index = 0

        for message in messages:

            name = getattr(contacts[index].profile, 'name', "")

            text = ""

            match message.type:
                case 'text':
                    process_app_msg(message.wa_from, name, message.id, message.text.body)
                    text = message.text.body
                case 'button':
                    process_app_button_pressed(message.wa_from, name, message.id, message.button)
                    text = message.button.payload
                case _:
                    # message with unhandled type
                    # print message for debugging
                    logger.warn("Received unhandled message type: %s", message.type)
                    text = "Unhandled"
                    try:
                        serialized_msg = WebhookMessageSerializer(instance=message)
                        logger.warn("Unhandled message: %s", str(serialized_msg.data))
                    except Exception as error:
                        logger.error("Failed to serialize message object", str(error))
            

            ReceivedMessages.objects.create(
                wamid = message.id,
                user_number = message.wa_from,
                user_wa_id = contacts[index].wa_id,
                message_type = message.type,
                message_text = text
            )

            # send read report
            success = send_read_report(message.id)

            # mark read in database
            ReceivedMessages.objects.filter(wamid=message.id).update(read=True, read_notified=success)

            index += 1

    def on_status_update(self, request, account_id, metatdata, statuses):
        logger.debug("Statuses received")

        for status in statuses:
            SentMessages.objects.filter(wamid=status.id).update(status=status.status)

    #receive and accept registration request
    def get(self, request):
        
        mode = request.query_params.get("hub.mode", None)
        token = request.query_params.get("hub.verify_token", None)
        challenge = int(request.query_params.get("hub.challenge", None))

        if mode and token:
            if mode == "subscribe" and token == verify_token:
                logger.info("Accepting webhook subscription.")
                return Response(challenge, status=status.HTTP_200_OK)
            else:
                logger.error("Failed to verify webhook subscription.")
                return Response(None, status=status.HTTP_403_FORBIDDEN)
        else:
            logger.error("Improper webhook subscription request.")
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        

# process app message as async task
def process_app_msg(
    user_num: str,
    name: str,
    wamid: str,
    message: str
):
    logger.debug("Processing received message: user number: %s", user_num)

    process_whatsapp_state_input.delay(user_num, name, wamid, message)


def process_app_button_pressed(
    user_num: str,
    name: str,
    wamid: str,
    button: Webhook.Entry.Change.Value.Message.Button
):
    logger.debug("Processing received button message: user number: %s", user_num)

    match button.payload.lower():
        case 'stop promotions':
            Profile.objects.filter(user__phone_number=user_num).update(stop_promotions=True)
            message = "You have opted out from receiving promotional messages. You will no longer receive such messages."
            send_app_text.delay(user_num, message, wamid)
        case _:
            logger.warn("Unhandled button pressed. Payload: %s", button.payload)