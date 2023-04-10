from rest_framework import serializers
from .models import MessageSuccessResponse, Webhook

## Serializer classes for the webhook

# class Webhook:
#     def __init__(self, object, entry):
#         self.object = object
#         self.entry = entry

#     class Error:
#         def __init__(self, code, title, message, error_data):
#             self.code = code
#             self.title = title
#             self.message = message
#             self.error_data = error_data

#         class Error_data:
#             def __init__(self, details) -> None:
#                 self.details = details

#     class Entry:
#         def __init__(self, id, changes):
#             self.id = id
#             self.changes = changes

#         class Change:
#             def __init__(self, value, field):
#                 self.value = value
#                 self.field = field

#             class Value:
#                 def __init__(self, messgaing_product, metadata, contacts=None, errors=None, messages=None, statuses=None):
#                     self.messaging_product = messgaing_product
#                     self.metadata = metadata
#                     self.contacts = contacts
#                     self.errors = errors
#                     self.messages = messages
#                     self.statuses = statuses

#                 class Metadata:
#                     def __init__(self, display_phone_number, phone_number_id):
#                         self.display_phone_number = display_phone_number
#                         self.phone_number_id = phone_number_id

#                 class Contact:
#                     def __init__(self, wa_id, profile):
#                         self.wa_id = wa_id
#                         self.profile = profile

#                     class Profile:
#                         def __init__(self, name):
#                             self.name = name


#                 class Message:
#                     def __init__(self, id, wa_from, type, audio=None, button=None, context=None,
#                                  document=None, errors=None, identity=None, image=None, interactive=None,
#                                  order=None, referral=None, sticker=None, system=None, text=None,
#                                  timestamp=None, video=None):
#                         self.id = id
#                         self.wa_from = wa_from
#                         self.type = type
#                         self.audio = audio
#                         self.button = button
#                         self.context = context
#                         self.document = document
#                         self.errors = errors
#                         self.identity = identity
#                         self.image = image
#                         self.interactive = interactive
#                         self.order = order
#                         self.referral = referral
#                         self.sticker = sticker
#                         self.system = system
#                         self.text = text
#                         self.timestamp = timestamp
#                         self.video = video
                    
#                     class Audio:
#                         def __init__(self, id, mime_type):
#                             self.id = id
#                             self.mime_type = mime_type

#                     class Button:
#                         def __init__(self, payload, text):
#                             self.payload = payload
#                             self.text = text
                    
#                     class Context:
#                         def __init__(self, forwarded, frequently_forwarded, wa_from, id, referred_product):
#                             self.forwarded = forwarded
#                             self.frequently_forwarded = frequently_forwarded
#                             self.wa_from = wa_from
#                             self.id = id
#                             self.referred_product = referred_product

#                         class ReferredProduct:
#                             def __init__(self, catalog_id, product_retailer_id) -> None:
#                                 self.catalog_id = catalog_id
#                                 self.product_retailer_id = product_retailer_id

#                     class Document:
#                         def __init__(self, id, caption, filename, sha256, mime_type):
#                             self.id = id
#                             self.caption = caption
#                             self.filename = filename
#                             self.sha256 = sha256
#                             self.mime_type = mime_type

#                     class Identity:
#                         def __init__(self, acknowledged, created_timestamp, hash):
#                             self.acknowledged = acknowledged
#                             self.created_timestamp = created_timestamp
#                             self.hash = hash

#                     class Image:
#                         def __init__(self, id, caption, sha256, mime_type):
#                             self.id = id
#                             self.caption = caption
#                             self.sha256 = sha256
#                             self.mime_type = mime_type
                
#                     class Interactive:
#                         def __init__(self, type):
#                             self.type = type

#                         class Type:
#                             def __init__(self, button_reply, list_reply):
#                                 self.button_reply
#                                 self.list_reply
                            
#                             class ButtonReply:
#                                 def __init__(self, id, title):
#                                     self.id = id
#                                     self.title = title

#                             class ListReply:
#                                 def __init__(self, id, title, description):
#                                     self.id = id
#                                     self.title = title
#                                     self.description = description
                    
#                     class Order:
#                         def __init__(self, catalog_id, text, product_items):
#                             self.catalog_id = catalog_id
#                             self.text = text
#                             self.product_items = product_items
                        
#                         class ProductItem:
#                             def __init__(self, product_retailer_id, quantity, item_price, currency):
#                                 self.product_retailer_id = product_retailer_id
#                                 self.quantity = quantity
#                                 self.item_price = item_price
#                                 self.currency = currency

#                     class Referral:
#                         def __init__(self, source_url, source_type, source_id, headline, body, media_type=None, image_url=None, video_url=None, thumbnail_url=None):
#                             self.source_url = source_url
#                             self.source_type = source_type
#                             self.source_id = source_id
#                             self.headline = headline
#                             self.body = body
#                             self.media_type = media_type
#                             self.image_url = image_url
#                             self.video_url = video_url
#                             self.thumbnail_url = thumbnail_url

#                     class Sticker:
#                         def __init__(self, id, mime_type, sha256, animated):
#                             self.id = id
#                             self.mime_type = mime_type
#                             self.sha256 = sha256
#                             self.animated = animated

#                     class System:
#                         def __init__(self, body, identity,  wa_id, type, customer, new_wa_id=None):
#                             self.body = body
#                             self.identity = identity
#                             self.new_wa_id = new_wa_id
#                             self.wa_id = wa_id
#                             self.type = type
#                             self.customer = customer

#                     class Text:
#                         def __init__(self, body):
#                             self.body

#                     class Video:
#                         def __init__(self, id, filename, sha256, caption, mime_type):
#                             self.id = id
#                             self.filename = filename
#                             self.sha256 = sha256
#                             self.caption = caption
#                             self.mime_type = mime_type

#                 class Status:                        
#                     def __init__(self, id=None, conversation=None, pricing=None, errors=None, recipient_id=None, status=None, timestamp=None):
#                         self.id = id
#                         self.conversation = conversation
#                         self.pricing = pricing
#                         self.errors = errors
#                         self.recipient_id = recipient_id
#                         self.status = status
#                         self.timestamp = timestamp
                    
#                     class Conversation:
#                         def __init__(self, id, origin, expiration_timestamp):
#                             self.id = id
#                             self.origin = origin
#                             self.expiration_timestamp = expiration_timestamp

#                         class Origin:
#                             def __init__(self, type):
#                                 self.type = type

#                     class Pricing:
#                         def __init__(self, category, pricing_model):
#                             self.category = category
#                             self.pricing_model = pricing_model


class WebhookErrorDataSerializer(serializers.Serializer):
    details = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Error.ErrorData(**validated_data)

class WebhookErrorSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    title = serializers.CharField()
    message = serializers.CharField()
    error_data = WebhookErrorDataSerializer()

    def create(self, validated_data):
        error_data_data = validated_data.pop("error_data")
        error_data = WebhookErrorDataSerializer(data=error_data_data)
        error_data.is_valid(raise_exception=True)
        return Webhook.Error(**validated_data, error_data=error_data.save())
    

class WebhookStatusPricingSerializer(serializers.Serializer):
    billable = serializers.BooleanField()
    category = serializers.CharField()
    pricing_model = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Status.Pricing(**validated_data)
    
class WebhookStatusConversationOriginSerializer(serializers.Serializer):
    type = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Status.Conversation.Origin(**validated_data)
    
class WebhookStatusConversationSerializer(serializers.Serializer):
    id = serializers.CharField()
    origin = WebhookStatusConversationOriginSerializer()
    expiration_timestamp = serializers.CharField(required=False)

    def create(self, validated_data):
        origin_data = validated_data.pop("origin")
        origin = WebhookStatusConversationOriginSerializer(data=origin_data)
        origin.is_valid(raise_exception=True)
        return Webhook.Entry.Change.Value.Status.Conversation(**validated_data, origin=origin.save())

class WebhookStatusSerializer(serializers.Serializer):
    id = serializers.CharField()
    conversation = WebhookStatusConversationSerializer(required=False)
    pricing = WebhookStatusPricingSerializer(required=False)
    errors = WebhookErrorSerializer(many=True, required=False)
    recipient_id = serializers.CharField()
    status = serializers.CharField()
    timestamp = serializers.IntegerField()

    def create(self, validated_data):
        #conversation
        conversation_data = validated_data.pop("conversation", None)
        if conversation_data:
            conversation = WebhookStatusConversationSerializer(data=conversation_data)
            conversation.is_valid(raise_exception=True)
            conversation = conversation.save()
        else:
            conversation = None
        #pricing
        pricing_data = validated_data.pop("pricing", None)
        if pricing_data:
            pricing = WebhookStatusPricingSerializer(data=pricing_data)
            pricing.is_valid(raise_exception=True)
            pricing = pricing.save()
        else:
            pricing = None
        #errors
        errors_data = validated_data.pop("errors",None)
        if errors_data:
            errors = []            
            for error_data in errors_data:
                error = WebhookErrorSerializer(data=error_data)
                error.is_valid(raise_exception=True)
                errors.append(error.save)
        else:
            errors = None
        return Webhook.Entry.Change.Value.Status(**validated_data, conversation=conversation, errors=errors, pricing=pricing)

class WebhookVideoSerializer(serializers.Serializer):
    id = serializers.CharField()
    caption = serializers.CharField()
    filename = serializers.CharField()
    sha256 = serializers.CharField()
    mime_type = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Video(**validated_data)

class WebhookSystemSerializer(serializers.Serializer):
    body = serializers.CharField()
    identity = serializers.CharField()
    new_wa_id = serializers.CharField()
    wa_id = serializers.CharField()
    type = serializers.CharField()
    customer = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.System(**validated_data)

class WebhookStickerSerializer(serializers.Serializer):
    id = serializers.CharField()
    animated = serializers.BooleanField()
    sha256 = serializers.CharField()
    mime_type = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Sticker(**validated_data)

class WebhookReferralSerializer(serializers.Serializer):
    source_url = serializers.CharField()
    source_type = serializers.CharField()
    source_id = serializers.CharField()
    headline = serializers.CharField()
    body = serializers.CharField()
    media_type = serializers.CharField()
    image_url = serializers.CharField()
    video_url = serializers.CharField()
    thumbnail_url = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Referral(**validated_data)


class WebhookOrderProductItemSerializer(serializers.Serializer):
    product_retailer_id = serializers.CharField()
    quantity = serializers.CharField()
    item_price = serializers.CharField()
    currency = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Order.ProductItem(**validated_data)

class WebhookOrderSerializer(serializers.Serializer):
    catalog_id = serializers.CharField()
    text = serializers.CharField()
    product_items = WebhookOrderProductItemSerializer(many=True)

    def create(self, validated_data):
        product_items_data = validated_data.pop("product_items")
        product_items = []
        for product_item_data in product_items_data:
            product_item = WebhookOrderProductItemSerializer(data=product_item_data)
            product_item.is_valid(raise_exception=True)
            product_items.append(product_item.save())
        return Webhook.Entry.Change.Value.Message.Order(**validated_data, product_items=product_items)

class WebhookInteractiveButtonReplySerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Interactive.Type.ButtonReply(**validated_data)
    
class WebhookInteractiveListReplySerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Interactive.Type.ListReply(**validated_data)

class WebhookInteractiveTypeSerializer(serializers.Serializer):
    list_reply = WebhookInteractiveListReplySerializer(required=False)
    button_reply = WebhookInteractiveButtonReplySerializer(required=False)

    def create(self, validated_data):
        list_reply_data = validated_data.pop("list_reply", None)
        if list_reply_data:
            list_reply = WebhookInteractiveListReplySerializer(data=list_reply_data)
            list_reply.is_valid(raise_exception=True)
            list_reply = list_reply.save()
        else:
            list_reply = None
        button_reply_data = validated_data.pop("button_reply", None)
        if button_reply_data:
            button_reply = WebhookInteractiveButtonReplySerializer(data=button_reply_data)
            button_reply.is_valid(raise_exception=True)
            button_reply = button_reply.save()
        else:
            button_reply = None
        return Webhook.Entry.Change.Value.Message.Interactive.Type(button_reply=button_reply, list_reply=list_reply)

class WebhookInteractiveSerializer(serializers.Serializer):
    type = WebhookInteractiveTypeSerializer()

    def create(self, validated_data):
        type_data = validated_data.pop("type")
        type = WebhookInteractiveTypeSerializer(data=type_data)
        type.is_valid(raise_exception=True)
        return Webhook.Entry.Change.Value.Message.Interactive(type=type)

class WebhookImageSerializer(serializers.Serializer):
    id = serializers.CharField()
    caption = serializers.CharField()
    sha256 = serializers.CharField()
    mime_type = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Image(**validated_data)

class WebhookIdentitySerializer(serializers.Serializer):
    acknowledged = serializers.CharField()
    created_timestamp = serializers.CharField()
    hash = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Identity(**validated_data)

class WebhookDocumentSerializer(serializers.Serializer):
    id = serializers.CharField()
    caption = serializers.CharField()
    filename = serializers.CharField()
    sha256 = serializers.CharField()
    mime_type = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Document(**validated_data)
    

class WebhookReferredProductSerializer(serializers.Serializer):
    catalog_id = serializers.CharField()
    product_retailer_id = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Context.ReferredProduct(**validated_data)

class WebhookContextSerializer(serializers.Serializer):
    forwarded = serializers.BooleanField()
    frequently_forwarded = serializers.BooleanField()
    vars()["from"] = serializers.CharField()
    id = serializers.CharField()
    referred_product = WebhookReferredProductSerializer(required=False)

    def create(self, validated_data):
        wa_from = validated_data.pop("from")
        referred_product_data = validated_data.pop("referred_product", None)
        if referred_product_data:
            referred_product = WebhookReferredProductSerializer(data=referred_product_data)
            referred_product.is_valid(raise_exception=True)
            referred_product = referred_product.save()
        else:
            referred_product = None
        return Webhook.Entry.Change.Value.Message.Context(**validated_data, wa_from=wa_from, referred_product=referred_product)


class WebhookAudioSerializer(serializers.Serializer):
    id = serializers.CharField()
    mime_type = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Audio(**validated_data)

class WebhookButtonSerializer(serializers.Serializer):
    payload = serializers.CharField()
    text = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Button(**validated_data)

class WebhookTextSerializer(serializers.Serializer):
    body = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Message.Text(**validated_data)

class WebhookMessageSerializer(serializers.Serializer):
    id = serializers.CharField()
    vars()["from"] = serializers.CharField()
    type = serializers.CharField()
    timestamp = serializers.CharField()
    audio = WebhookAudioSerializer(required=False)
    button = WebhookButtonSerializer(required=False)
    context = WebhookContextSerializer(required=False)
    document = WebhookDocumentSerializer(required=False)
    errors = WebhookErrorSerializer(many=True, required=False)
    identity = WebhookIdentitySerializer(required=False)
    image = WebhookImageSerializer(required=False)
    interactive = WebhookInteractiveSerializer(required=False)
    order = WebhookOrderSerializer(required=False)
    referral = WebhookReferralSerializer(required=False)
    sticker = WebhookStickerSerializer(required=False)
    system = WebhookSystemSerializer(required=False)
    text = WebhookTextSerializer(required=False)
    video = WebhookVideoSerializer(required=False)

    def create(self, validated_data):
        wa_from = validated_data.pop("from")
        #Audio
        audio_data = validated_data.pop("audio", None)
        if audio_data:
            audio = WebhookAudioSerializer(data=audio_data)
            audio.is_valid(raise_exception=True)
            audio = audio.save()
        else:
            audio = None
        #Button
        button_data = validated_data.pop("button", None)
        if button_data:
            button = WebhookButtonSerializer(data=button_data)
            button.is_valid(raise_exception=True)
            button = button.save()
        else:
            button = None
        #Text
        text_data = validated_data.pop("text", None)
        if text_data:
            text = WebhookTextSerializer(data=text_data)
            text.is_valid(raise_exception=True)
            text = text.save()
        else:
            text = None
        #Errors
        errors_data = validated_data.pop("errors",None)
        if errors_data:
            errors = []            
            for error_data in errors_data:
                error = WebhookErrorSerializer(data=error_data)
                error.is_valid(raise_exception=True)
                errors.append(error.save)
        else:
            errors = None
        #Context
        context_data = validated_data.pop("context", None)
        if context_data:
            context = WebhookContextSerializer(data=context_data)
            context.is_valid(raise_exception=True)
            context = context.save()
        else:
            context = None
        #Document
        document_data = validated_data.pop("document", None)
        if document_data:
            document = WebhookDocumentSerializer(data=document_data)
            document.is_valid(raise_exception=True)
            document = document.save()
        else:
            document = None
        #Identity
        identity_data = validated_data.pop("identity", None)
        if identity_data:
            identity = WebhookIdentitySerializer(data=identity_data)
            identity.is_valid(raise_exception=True)
            identity = identity.save()
        else:
            identity = None
        #Image
        image_data = validated_data.pop("image", None)
        if image_data:
            image = WebhookImageSerializer(data=image_data)
            image.is_valid(raise_exception=True)
            image = image.save()
        else:
            image = None
        #Interactive
        interactive_data = validated_data.pop("interactive", None)
        if interactive_data:
            interactive = WebhookInteractiveSerializer(data=interactive_data)
            interactive.is_valid(raise_exception=True)
            interactive = interactive.save()
        else:
            interactive = None
        #Order
        order_data = validated_data.pop("order", None)
        if order_data:
            order = WebhookOrderSerializer(data=order_data)
            order.is_valid(raise_exception=True)
            order = order.save()
        else:
            order = None
        #Referral
        referral_data = validated_data.pop("referral", None)
        if referral_data:
            referral = WebhookReferralSerializer(data=referral_data)
            referral.is_valid(raise_exception=True)
            referral = referral.save()
        else:
            referral = None
        #sticker
        sticker_data = validated_data.pop("sticker", None)
        if sticker_data:
            sticker = WebhookStickerSerializer(data=sticker_data)
            sticker.is_valid(raise_exception=True)
            sticker = referral.save()
        else:
            sticker = None
        #System
        system_data = validated_data.pop("system", None)
        if system_data:
            system = WebhookSystemSerializer(data=system_data)
            system.is_valid(raise_exception=True)
            system = referral.save()
        else:
            system = None
        #Video
        video_data = validated_data.pop("video", None)
        if video_data:
            video = WebhookVideoSerializer(data=video_data)
            video.is_valid(raise_exception=True)
            video = referral.save()
        else:
            video = None

        return Webhook.Entry.Change.Value.Message(**validated_data, wa_from=wa_from, audio=audio, button=button,
                                                context=context, text=text, document=document, identity=identity,
                                                image=image, interactive=interactive, order=order, referral=referral,
                                                sticker=sticker, system=system, video=video, errors=errors)


class WebhookProfileSerializer(serializers.Serializer):
    name = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Contact.Profile(**validated_data)
    
class WebhookContactSerializer(serializers.Serializer):
    wa_id = serializers.CharField()
    profile = WebhookProfileSerializer()

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        profile = WebhookProfileSerializer(data=profile_data)
        profile.is_valid(raise_exception=True)
        return Webhook.Entry.Change.Value.Contact(**validated_data, profile=profile.save())

class WebhookMetadataSerializer(serializers.Serializer):
    display_phone_number = serializers.CharField()
    phone_number_id = serializers.CharField()

    def create(self, validated_data):
        return Webhook.Entry.Change.Value.Metadata(**validated_data)


class WebhookValueSerializer(serializers.Serializer):
    messaging_product = serializers.CharField()
    metadata = WebhookMetadataSerializer()
    contacts = WebhookContactSerializer(many=True, required=False)
    errors = WebhookErrorSerializer(many=True, required=False)
    messages = WebhookMessageSerializer(many=True, required=False)
    statuses = WebhookStatusSerializer(many=True, required=False)

    def create(self, validated_data):
        #metadata
        metadata_data = validated_data.pop("metadata")
        metadata = WebhookMetadataSerializer(data=metadata_data)
        metadata.is_valid(raise_exception=True)
        #contacts
        contacts_data = validated_data.pop("contacts", None)
        if contacts_data:
            contacts = []
            for contact_data in contacts_data:
                contact = WebhookContactSerializer(data=contact_data)
                contact.is_valid(raise_exception=True)
                contacts.append(contact.save())
        else:
            contacts = None
        #errors
        errors_data = validated_data.pop("errors", None)
        if errors_data:
            errors = []
            for error_data in errors_data:
                error = WebhookErrorSerializer(data=error_data)
                error.is_valid(raise_exception=True)
                errors.append(error.save())
        else:
            errors = None
        #messages
        messages_data = validated_data.pop("messages", None)
        if messages_data:
            messages = []
            for message_data in messages_data:
                message = WebhookMessageSerializer(data=message_data)
                message.is_valid(raise_exception=True)
                messages.append(message.save())
        else:
            messages = None
        #statuses
        statuses_data = validated_data.pop("statuses", None)
        if statuses_data:
            statuses = []
            for status_data in statuses_data:
                status = WebhookStatusSerializer(data=status_data)
                status.is_valid(raise_exception=True)
                statuses.append(status.save())
        else:
            statuses = None
        return Webhook.Entry.Change.Value(**validated_data, metadata=metadata.save(), contacts=contacts, messages=messages, statuses=statuses, errors=errors)

class WebhookChangeSerializer(serializers.Serializer):
    field = serializers.CharField()
    value = WebhookValueSerializer()

    def create(self, validated_data):
        value_data = validated_data.pop("value")
        value = WebhookValueSerializer(data=value_data)
        value.is_valid(raise_exception=True)
        return Webhook.Entry.Change(**validated_data, value=value.save())

class WebhookEntrySerializer(serializers.Serializer):
    id = serializers.CharField()
    changes = WebhookChangeSerializer(many=True)

    def create(self, validated_data):
        changes_data = validated_data.pop("changes")
        changes = []
        for change_data in changes_data:
            change = WebhookChangeSerializer(data=change_data)
            change.is_valid(raise_exception=True)
            changes.append(change.save())
        return Webhook.Entry(**validated_data, changes=changes)

class WebhookObjectSerializer(serializers.Serializer):
    object = serializers.CharField()
    entry = WebhookEntrySerializer(many=True)

    def create(self, validated_data):
        entry_data = validated_data.pop("entry")
        entry = []
        for an_entry_data in entry_data:
            an_entry = WebhookEntrySerializer(data=an_entry_data)
            an_entry.is_valid(raise_exception=True)
            entry.append(an_entry.save())
        return Webhook(**validated_data, entry=entry)

## Serializer for the messages endpoint successful response
class ResponseMessageSerializer(serializers.Serializer):
    id = serializers.CharField()

    def create(self, validated_data):
        return MessageSuccessResponse.Message(**validated_data)
    
class ResponseContactSerializer(serializers.Serializer):
    input = serializers.CharField()
    wa_id = serializers.CharField()

    def create(self, validated_data):
        return MessageSuccessResponse.Contact(**validated_data)

class MessageSuccessResponseSerializer(serializers.Serializer):
    contacts = ResponseContactSerializer(many=True)
    messages = ResponseMessageSerializer(many=True)

    def create(self, validated_data):
        messages_data = validated_data.pop("messages")
        contacts_data = validated_data.pop("contacts")
        messages = []
        for message_data in messages_data:
            message = ResponseMessageSerializer(data=message_data)
            message.is_valid(raise_exception=True)
            messages.append(message.save())
        contacts = []
        for contact_data in contacts_data:
            contact = ResponseContactSerializer(data=contact_data)
            contact.is_valid()
            contacts.append(contact.save())
        return MessageSuccessResponse(contacts, messages)


# Serializer classes for message sending

class LanguageSerializer(serializers.Serializer):
    code = serializers.CharField()

class TextSerializer(serializers.Serializer):
    body = serializers.CharField()
    preview_url = serializers.BooleanField()

class ContextSerializer(serializers.Serializer):
    message_id = serializers.CharField()

class ParameterSerializer(serializers.Serializer):
    type = serializers.CharField()
    text = serializers.CharField()

class ComponentSerializer(serializers.Serializer):
    type = serializers.CharField()
    sub_type = serializers.CharField(required=False)
    parameters = ParameterSerializer(many=True)
    index = serializers.CharField(required=False)

class TemplateSerializer(serializers.Serializer):
    name = serializers.CharField()
    language = LanguageSerializer()
    components = ComponentSerializer(many=True, required=False)

class MessageSerializer(serializers.Serializer):
    to = serializers.CharField()
    type = serializers.CharField()
    messaging_product = serializers.CharField()
    recipient_type = serializers.CharField()
    template = TemplateSerializer(required=False)
    text = TextSerializer(required=False)
    status = serializers.CharField()
    context = ContextSerializer(required=False)