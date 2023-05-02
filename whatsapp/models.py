from django.db import models


# Create your models here.

## database models
class SentMessages(models.Model):
    wamid = models.CharField(max_length=256, null=True)
    user_number = models.CharField(max_length=15)
    user_wa_id = models.CharField(max_length=128)
    message_type = models.CharField(max_length=128)
    message_text = models.TextField(null=True, default=None)
    template_name = models.CharField(max_length=128, null=True, default=None)
    status = models.CharField(max_length=50, null=True)
    created = models.DateTimeField(auto_now_add=True)


class ReceivedMessages(models.Model):
    wamid = models.CharField(max_length=256, null=True)
    user_number = models.CharField(max_length=15)
    user_wa_id = models.CharField(max_length=128)
    message_type = models.CharField(max_length=128)
    message_text = models.TextField(null=True, default=None)
    read = models.BooleanField(default=False)
    read_notified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


# class for message sending

class Message():
    def __init__(self, to, type, messaging_product="whatsapp", recipient_type="individual",
                 text=None, template=None, status=None, context=None):
        self.to = to
        self.type = type
        self.messaging_product = messaging_product
        self.recipient_type = recipient_type
        self.template = template
        self.text = text
        self.status = status
        self.context = context

    class Template:
        def __init__(self, name, language, components=None):
            self.name = name
            self.language = language
            self.components = components

        class Language:
            def __init__(self, code):
                self.code = code
                    
        class Component:
            def __init__(self, type="body", parameters=None, sub_type=None, index=None):
                self.type = type
                self.sub_type =sub_type
                self.parameters = parameters
                self.index = index

            class Parameter:
                def __init__(self, type, text):
                    self.type = type
                    self.text = text
    
    class Text:
        def __init__(self, body, preview_url=False):
            self.body = body
            self.preview_url = preview_url

    class Context:
        def __init__(self, message_id):
            self.message_id = message_id


## class for the webhook object

# {
#   "object": "whatsapp_business_account",
#   "entry": [{
#     "id": "WHATSAPP-BUSINESS-ACCOUNT-ID",
#     "changes": [{
#       "value": {
#          "messaging_product": "whatsapp",
#          "metadata": {
#            "display_phone_number": "PHONE-NUMBER",
#            "phone_number_id": "PHONE-NUMBER-ID"
#          },
#       # Additional arrays and objects
#          "contacts": [{...}]
#          "errors": [{...}]
#          "messages": [{...}]
#          "statuses": [{...}]
#       },
#       "field": "messages"
#     }]
#   }]
# }

class Webhook:
    def __init__(self, object, entry):
        self.object = object
        self.entry = entry

    class Error:
        def __init__(self, code, title, message, error_data):
            self.code = code
            self.title = title
            self.message = message
            self.error_data = error_data

        class ErrorData:
            def __init__(self, details) -> None:
                self.details = details

    class Entry:
        def __init__(self, id, changes):
            self.id = id
            self.changes = changes

        class Change:
            def __init__(self, value, field):
                self.value = value
                self.field = field

            class Value:
                def __init__(self, messaging_product, metadata, contacts=None, errors=None, messages=None, statuses=None):
                    self.messaging_product = messaging_product
                    self.metadata = metadata
                    self.contacts = contacts
                    self.errors = errors
                    self.messages = messages
                    self.statuses = statuses

                class Metadata:
                    def __init__(self, display_phone_number, phone_number_id):
                        self.display_phone_number = display_phone_number
                        self.phone_number_id = phone_number_id

                class Contact:
                    def __init__(self, wa_id, profile):
                        self.wa_id = wa_id
                        self.profile = profile

                    class Profile:
                        def __init__(self, name):
                            self.name = name


                class Message:
                    def __init__(self, id, wa_from, type, audio=None, button=None, context=None,
                                 document=None, errors=None, identity=None, image=None, interactive=None,
                                 order=None, referral=None, sticker=None, system=None, text=None,
                                 timestamp=None, video=None):
                        self.id = id
                        self.wa_from = wa_from
                        self.type = type
                        self.audio = audio
                        self.button = button
                        self.context = context
                        self.document = document
                        self.errors = errors
                        self.identity = identity
                        self.image = image
                        self.interactive = interactive
                        self.order = order
                        self.referral = referral
                        self.sticker = sticker
                        self.system = system
                        self.text = text
                        self.timestamp = timestamp
                        self.video = video
                    
                    class Audio:
                        def __init__(self, id, mime_type):
                            self.id = id
                            self.mime_type = mime_type

                    class Button:
                        def __init__(self, payload, text):
                            self.payload = payload
                            self.text = text
                    
                    class Context:
                        def __init__(self, forwarded=None, frequently_forwarded=None, wa_from=None, id=None, referred_product=None):
                            self.forwarded = forwarded
                            self.frequently_forwarded = frequently_forwarded
                            self.wa_from = wa_from
                            self.id = id
                            self.referred_product = referred_product

                        class ReferredProduct:
                            def __init__(self, catalog_id=None, product_retailer_id=None) -> None:
                                self.catalog_id = catalog_id
                                self.product_retailer_id = product_retailer_id

                    class Document:
                        def __init__(self, id=None, caption=None, filename=None, sha256=None, mime_type=None):
                            self.id = id
                            self.caption = caption
                            self.filename = filename
                            self.sha256 = sha256
                            self.mime_type = mime_type

                    class Identity:
                        def __init__(self, acknowledged, created_timestamp, hash):
                            self.acknowledged = acknowledged
                            self.created_timestamp = created_timestamp
                            self.hash = hash

                    class Image:
                        def __init__(self, id=None, caption=None, sha256=None, mime_type=None):
                            self.id = id
                            self.caption = caption
                            self.sha256 = sha256
                            self.mime_type = mime_type
                
                    class Interactive:
                        def __init__(self, type):
                            self.type = type

                        class Type:
                            def __init__(self, button_reply=None, list_reply=None):
                                self.button_reply = button_reply
                                self.list_reply = list_reply
                            
                            class ButtonReply:
                                def __init__(self, id, title):
                                    self.id = id
                                    self.title = title

                            class ListReply:
                                def __init__(self, id, title, description):
                                    self.id = id
                                    self.title = title
                                    self.description = description
                    
                    class Order:
                        def __init__(self, catalog_id, text, product_items):
                            self.catalog_id = catalog_id
                            self.text = text
                            self.product_items = product_items
                        
                        class ProductItem:
                            def __init__(self, product_retailer_id, quantity, item_price, currency):
                                self.product_retailer_id = product_retailer_id
                                self.quantity = quantity
                                self.item_price = item_price
                                self.currency = currency

                    class Referral:
                        def __init__(self, source_url, source_type, source_id, headline, body, media_type=None, image_url=None, video_url=None, thumbnail_url=None):
                            self.source_url = source_url
                            self.source_type = source_type
                            self.source_id = source_id
                            self.headline = headline
                            self.body = body
                            self.media_type = media_type
                            self.image_url = image_url
                            self.video_url = video_url
                            self.thumbnail_url = thumbnail_url

                    class Sticker:
                        def __init__(self, id, mime_type, sha256, animated):
                            self.id = id
                            self.mime_type = mime_type
                            self.sha256 = sha256
                            self.animated = animated

                    class System:
                        def __init__(self, body=None, identity=None,  wa_id=None, type=None, customer=None, new_wa_id=None):
                            self.body = body
                            self.identity = identity
                            self.new_wa_id = new_wa_id
                            self.wa_id = wa_id
                            self.type = type
                            self.customer = customer

                    class Text:
                        def __init__(self, body):
                            self.body = body

                    class Video:
                        def __init__(self, id=None, filename=None, sha256=None, caption=None, mime_type=None):
                            self.id = id
                            self.filename = filename
                            self.sha256 = sha256
                            self.caption = caption
                            self.mime_type = mime_type

                class Status:                        
                    def __init__(self, id=None, conversation=None, pricing=None, errors=None, recipient_id=None, status=None, timestamp=None):
                        self.id = id
                        self.conversation = conversation
                        self.pricing = pricing
                        self.errors = errors
                        self.recipient_id = recipient_id
                        self.status = status
                        self.timestamp = timestamp
                    
                    class Conversation:
                        def __init__(self, id, origin, expiration_timestamp=None):
                            self.id = id
                            self.origin = origin
                            self.expiration_timestamp = expiration_timestamp

                        class Origin:
                            def __init__(self, type):
                                self.type = type

                    class Pricing:
                        def __init__(self, billable, category, pricing_model):
                            self.billable = billable
                            self.category = category
                            self.pricing_model = pricing_model

## class for messages endpoint successful response

class MessageSuccessResponse:
    def __init__(self, contacts, messages):
        self.contacts = contacts
        self.messages = messages

    class Message:
        def __init__(self, id):
            self.id = id

    class Contact:
        def __init__(self, input, wa_id):
            self.input = input
            self.wa_id = wa_id


## class for error response

# {
#   "error": {
#     "message": "(#130429) Rate limit hit",
#     "type": "OAuthException",
#     "code": 130429,
#     "error_data": {
#         "messaging_product": "whatsapp", 
#         "details": "Message failed to send because there were too many messages sent from this phone number in a short period of time"
#     },
#     "error_subcode": 2494055,
#     "fbtrace_id": "Az8or2yhqkZfEZ-_4Qn_Bam"
#   }
# }

class ErrorResponse:
    def __init__(self, error):
        self.error = error

    class Error:
        def __init__(self, message, type, code, error_data, error_subcode, fbtrace_id):
            self.message = message
            self.type = type
            self.code = code
            self.error_data = error_data
            self.error_subcode = error_subcode
            self.fbtrace_id = fbtrace_id
        
        class ErrorData:
            def __init__(self, messaging_product, details):
                self.messaging_product = messaging_product
                self.details = details