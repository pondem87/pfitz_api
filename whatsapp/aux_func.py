from decouple import config
from whatsapp.models import Message, SentMessages
from whatsapp.serializers import MessageSerializer, MessageSuccessResponseSerializer
import requests
import logging

logger = logging.getLogger(__name__)

wa_temp_lang = config('WA_TEMPLATE_DEFAULT_LANG')

whatsapp_num_id = config('WHATSAPP_NUMBER_ID')
whatapp_bus_id = config('WHATSAPP_BUSINESS_ID')
whatsapp_access_token = config('WHATSAPP_ACCESS_TOKEN')
messages_url = "https://graph.facebook.com/v16.0/{num_id}/messages".format(num_id=whatsapp_num_id)
auth_header = "Bearer " + whatsapp_access_token

def send_template(dest, template, params=None, lang=wa_temp_lang):

    logger.debug("Running send_template")

    # create parameters array of objects if params not None
    parameters = []
    if params is not None:
        for param in params:
            parameters.append(Message.Template.Component.Parameter(**param))
    else:
        parameters = None
    
    # create template languge object
    language = Message.Template.Language(code=lang)

    # place parameters into template component
    # components can be set to None if there is no component
    if parameters is not None:
        components = [Message.Template.Component(parameters=parameters),]
    else:
        components = None

    # create template object
    template = Message.Template(name=template, language=language, components=components)

    # create message object
    message = Message(to=dest, type="template", template=template)

    # serialize
    send_to_messages_api(message)


def send_text(dest, message, reply_to_wamid=None, conv_id=None):

    # breaking change by whatsapp means I cannot reply to a message
    reply_to_wamid = None

    # create text obj
    text = Message.Text(body=message)

    # create context if replying to message
    context = None
    if reply_to_wamid is not None:
        context = Message.Context(message_id=reply_to_wamid)

    # generate messaging object
    msg_obj = Message(to=dest, type="text", text=text, context=context)

    # send to api
    send_to_messages_api(msg_obj)

    

def send_read_report(wamid):
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": wamid
    }

    headers = {
        "authorization": auth_header,
    }

    try:
        response = requests.post(messages_url, headers=headers, json=payload)

        logger.info("Read report response: %s", str(response.json()))
        
        success = response.json()["success"] if response.status_code == 200 else False

        if success:
            logger.info("Updated 'read' status for wamid: %s", wamid)
        else:
            logger.error("Failed status update for wamid: %s", wamid)

        return success
    
    except Exception as err:

        logger.error("Error when sending read notification: %s", str(err))
        return False



# send prepared message to messages endpoint
def send_to_messages_api(message):

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
                template_name = getattr(message.template, 'name', None),
                message_text = getattr(message.text, 'body', None),
                status = "sent"
            )
        except:
            logger.error("Failed to deserialize whatsapp messages api response: %s", str(serializer.errors))
    else:
        logger.error("Whatsapp request failed: %s", response.text)