from decouple import config
from whatsapp.models import Message, SentMessages
from whatsapp.serializers import MessageSerializer, MessageSuccessResponseSerializer
import logging

logger = logging.getLogger(__name__)

import requests

debug = config('DEBUG', default=True, cast=bool)
whatsapp_num_id = config('WHATSAPP_TEST_NUMBER_ID') if debug else config('WHATSAPP_NUMBER_ID')
whatapp_bus_id = config('WHATSAPP_TEST_BUSINESS_ID') if debug else config('WHATSAPP_BUSINESS_ID')
whatsapp_access_token = config('WHATSAPP_ACCESS_TOKEN')
messages_url = "https://graph.facebook.com/v16.0/{num_id}/messages".format(num_id=whatsapp_num_id)
auth_header = "Bearer " + whatsapp_access_token

def send_template(dest, template, params, lang="en_US"):

    logger.debug("Running send_template")

    # create parameters array of objects
    parameters = []
    for param in params:
        parameters.append(Message.Template.Component.Parameter(**param))
    
    # create template languge object
    language = Message.Template.Language(code=lang)

    # place parameters into template component
    components = [Message.Template.Component(parameters=parameters),]

    # create template object
    template = Message.Template(name=template, language=language, components=components)

    # create message object
    message = Message(to=dest, type="template", template=template)

    # serialize
    serialized = MessageSerializer(instance=message)

    logger.debug("Message serialized: %s", str(serialized.data))

    headers = {
        "authorization": auth_header,
    }

    response = requests.post(messages_url, headers=headers, json=serialized.data)

    if (response.status_code == 200):
        try:
            serializer = MessageSuccessResponseSerializer(data=response.json())
            serializer.is_valid(raise_exception=True)
            message_respone = serializer.save()
            
            # Save message details to database
            logger.info("Message to user: %s sent. wamid: %s", message.to, message_respone.messages[0].id)

            SentMessages.objects.create(
                wamid = message_respone.messages[0].id,
                user_number = message.to,
                user_wa_id = message_respone.contacts[0].wa_id,
                message_type = message.type,
                template_name = message.template.name,
                status = "sent"
            )
        except:
            logger.error("Failed to deserialize whatsapp messages api response: %s", str(serializer.errors))
    else:
        logger.error("Whatsaap request failed: %s", response.text)