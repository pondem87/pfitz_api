from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import WebhookObjectSerializer
from .models import SentMessages, ReceivedMessages
from decouple import config
import logging

logger = logging.getLogger(__name__)

verify_token = config('WA_WEBHOOK_VERIFY_TOKEN')

# Create your views here.
class WebhookAPIView(generics.GenericAPIView):

    #receive and process the webhook
    def post(self, request):

        logger.debug("Received webhook data: %s", str(request.data))
        
        serializer = WebhookObjectSerializer(data=request.data)
        if serializer.is_valid():
            webhook = serializer.save()
            
            if webhook.entry[0].changes[0].value.messages:
                self.on_message_received(request, webhook.entry[0].id, webhook.entry[0].changes[0].value.metadata, webhook.entry[0].changes[0].value.contacts, webhook.entry[0].changes[0].value.messages)
            elif webhook.entry[0].changes[0].value.statuses:
                self.on_status_update(request, webhook.entry[0].id, webhook.entry[0].changes[0].value.metadata, webhook.entry[0].changes[0].value.statuses)

            return Response(None, status=status.HTTP_200_OK)
        else:
            #parsing failed
            logger.error("Serialising webhook failed: %s", str(serializer.errors))
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        
    ## webhook events
    def on_message_received(self, request, account_id, metadata, contacts, messages):
        logger.debug("Messages received")

        #index to iterate contacts
        index = 0

        for message in messages:
            message_text = ''
            if message.text:
                message_text = message.text.body
            else:
                message_text = "No text available"

            ReceivedMessages.objects.create(
                wamid = message.id,
                user_number = message.wa_from,
                user_wa_id = contacts[index].wa_id,
                message_type = message.type,
                message_text = message_text
            )

            index += 1

    def on_status_update(self, request, account_id, metatdata, statuses):
        logger.debug("Statuses received")

        for status in statuses:
            SentMessages.objects.filter(wamid=status.id).update(status=status.status)

    #receive and accept registration request
    def get(self, request):
        
        mode = request.query_params.get("hub.mode", None)
        token = request.query_params.get("hub.verify_token", None)
        challenge = request.query_params.get("hub.challenge", None)

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