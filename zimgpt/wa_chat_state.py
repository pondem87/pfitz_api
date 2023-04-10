from whatsapp.aux_func import send_text
from django.contrib.auth import get_user_model
from decouple import config
from .aux_func import get_chat_completion, get_completion, process_ref_code
from rest_framework import serializers, status
from payments.models import Product, Payment
from payments.pay_func import initiate_payment, check_payment_status
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

model = config('OPENAI_COMPLETION_MODEL')
currency = config('BASE_CURRENCY')
chat_expiration_time = config('CHAT_EXPIRATION_TIME', cast=int)

## ChatState serializer

class WAChatStateDataProductSerializer(serializers.Serializer):
    index = serializers.IntegerField()
    product_id = serializers.UUIDField()
    units = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=15, decimal_places=2)

    def create(self, validated_data):
        return WAChatState.Data.Product(**validated_data)

class WAChatStateDataSerializer(serializers.Serializer):
    conv_history = serializers.CharField(required=False, allow_null=True)
    product_id = serializers.UUIDField(required=False, allow_null=True)
    payment_method = serializers.CharField(required=False, allow_null=True)
    payment_number = serializers.CharField(required=False, allow_null=True)
    product_list = WAChatStateDataProductSerializer(many=True, required=False, allow_null=True)

    def create(self, validated_data):
        product_list_data = validated_data.pop("product_list", None)
        if product_list_data:
            product_list = []
            for product_data in product_list_data:
                product = WAChatStateDataProductSerializer(**product_data)
                product.is_valid(raise_exception=True)
                product_list.append(product.save())
        else:
            product_list = None
        return WAChatState.Data(**validated_data, product_list=product_list)

class WAChatStateSerializer(serializers.Serializer):
    user_num = serializers.CharField()
    user_name = serializers.CharField(allow_blank=True)
    state = serializers.CharField()
    data = WAChatStateDataSerializer(required=False, allow_null=True)
    new_password = serializers.CharField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        data_data = validated_data.pop("data", None)
        if data_data:
            data = WAChatStateDataSerializer(data=data_data)
            data.is_valid(raise_exception=True)
            data = data.save()
        else:
            data = None
        return WAChatState(**validated_data, data=data)

# State machine object
class WAChatState:

    """ states """
    _START = "START"
    _GET_NAME = "GET_NAME"
    _MENU = "MENU"
    _CHAT = "CHAT"
    _FREE_PROMPT = "FREE_PROMPT"
    _CHOOSE_PRODUCT = "CHOOSE_PRODUCT"
    _CONFIRM_PRODUCT = "CONFIRM_PRODUCT"
    _GET_PAYMENT_METHOD = "GET_PAYMENT_METHOD"
    _GET_PAYMENT_NUMBER = "GET_PAYMENT_NUMBER"
    _CONFIRM_PAYMENT_DETAILS = "CONFIRM_PAYMENT_DETAILS"
    _CHECK_PAYMENT = "CHECK_PAYMENT"

    _menu_text = "\n\nReply with\n\n *1*: _for_ Chat (chat with AI)\n *2*: _for_ Free Prompt (send custom prompts to AI)" + \
        "\n *3*: _to_ View And Buy Tokens\n *4*: _to_ View Payments\n *5*: _to_ Get Free Tokens \n\nFor help, whatsapp 263775409679. For more functions: https://zimgpt.pfitz.co.zw/"
    _menu_vars = ['1', '2', '3', '4', '5']
    _reset_code = "*#exit"

    class Data:
        def __init__(self,
                    conv_history=None,
                    product_id=None,
                    product_list=None,
                    payment_method=None,
                    payment_number=None):
            self.conv_history = conv_history
            self.product_list = product_list
            self.product_id = product_id
            self.payment_method = payment_method
            self.payment_number = payment_number

        class Product:
            def __init__(self, index, product_id, units, price):
                self.index = index
                self.product_id = product_id
                self.units = units
                self.price = price

    def __init__(self, user_num, user_name="", state=_START, data=None, new_password=None, timestamp=timezone.now()):
        self.user_num = user_num
        self.user_name = user_name
        self.state = state
        self.data = data
        self.new_password = new_password
        self.timestamp = timestamp
    
    def check_reset_code(input: str) -> bool:
        if WAChatState._reset_code in input:
            return True
        else:
            return False
        
    def isTimeStampExpired(self):
        return timezone.now() - self.timestamp > timedelta(hours=chat_expiration_time)

    def transition(self, wamid, input):

        logger.debug("State transition called")

        # check for reset code
        if WAChatState.check_reset_code(input):
            self.state = WAChatState._START
            self.data = None

        if self.isTimeStampExpired():
            self.state = WAChatState._START
            self.data = None
            self.timestamp = timezone.now()

        match self.state:

            #### case 1: The ground state
            case WAChatState._START:
                # chat in ground state
                if self.new_password is not None:
                    # newly created user
                    # ask user for name
                    if len(self.user_name.strip()) > 0:
                        name_line = "Hi, {name}. Are you comfortable using this name?\n\n Enter another name if you want, or send *0* to continue with this name.".format(name=self.user_name)
                    else:
                        name_line = "Before we begin. What is your name?"
                    messages = [
                        "Welcome to ZimGPT, a service that allows you access to an AI with vast knowledge and the ability to understand and answer questions from any topic you can think of. Boost your creativity and productivity by interacting with the AI in plain english language.",
                        "You can also access the service online for better readability and copy-paste functionality for your projects and assignments.\n\n The link is https://zimgpt.pfitz.co.zw/ and login with the password in the message below. Keep the password safe as it is not saved in our system.",
                        "Password:{pwd}".format(pwd=self.new_password),
                        name_line
                    ]
                    for message in messages:
                        send_text(self.user_num, message)
                    # nonify password
                    self.new_password = None
                    # update state
                    self.state = WAChatState._GET_NAME
                    # procees ref code
                    process_ref_code(input)
                else:
                    user = get_user_model().objects.get(phone_number=self.user_num)
                    message = "Welcome back to ZimGPT, {name}. Remember you can also access this service online for better readability and copy-paste functionality for your projects and assignments using the link below.\n\n How may I assist you today?".format(name=user.name) + WAChatState._menu_text
                    send_text(self.user_num, message, wamid)
                    # update state
                    self.state = WAChatState._MENU

            #### case 2: Requesting for user's name after ground state
            case WAChatState._GET_NAME:

                if str(input) == '0':
                    if len(self.user_name.strip()) > 0:
                        # use whats app profile name
                        user = get_user_model().objects.get(phone_number=self.user_num)
                        user.name = self.user_name
                        user.save()
                        message = "Thank you, {name}. How may I assist you today?".format(name=self.user_name) + WAChatState._menu_text
                        send_text(self.user_num, message, wamid)
                        self.state = WAChatState._MENU

                    else:
                        message = "Name should only contain letters or numbers without spaces. Please note that full name and surname is not required. Keep it simple."
                        send_text(self.user_num, message, wamid)

                else: 
                    if not re.match("^\w+$", input):
                        # if name is not suitable do not send explanatory message and do not update state.
                        message = "Name should only contain letters or numbers without spaces. Please note that full name and surname is not required. Keep it simple."
                        send_text(self.user_num, message, wamid)
                    else:
                        # good name
                        user = get_user_model().objects.get(phone_number=self.user_num)
                        user.name = input
                        user.save()
                        message = "Thank you, {name}. How may I assist you today?".format(name=input) + WAChatState._menu_text
                        send_text(self.user_num, message, wamid)
                        self.state = WAChatState._MENU

            #### case 3: Checking menu selection
            case WAChatState._MENU:
                if str(input) in WAChatState._menu_vars:
                    match int(input):
                        case 1:
                            # selected chat
                            message = "You are in chat mode. Sending {code} will send you back to main menu.\n\n Hi. What's on your mind today?".format(code=WAChatState._reset_code)
                            send_text(self.user_num, message, wamid)
                            self.data = WAChatState.Data(conv_history=None)
                            self.state = WAChatState._CHAT
                        case 2:
                            # selected free response
                            message = "Free prompt mode. Sending {code} will send you back to main menu.\n\n You can enter any text for text-completion by the AI model. ({model})".format(code=WAChatState._reset_code, model=model)
                            send_text(self.user_num, message, wamid)
                            self.data = None
                            self.state = WAChatState._FREE_PROMPT
                        case 3:
                            # selected view and buy tokens
                            user = get_user_model().objects.get(phone_number=self.user_num)
                            product_list = [WAChatState.Data.Product(index + 1, product.uuid, product.units_offered, product.price) for index, product in enumerate(Product.objects.filter(active=True).order_by('price'))]
                            message = "Tokens remaining: *" + str(user.profile.tokens_remaining) + "*\n\n If you want to refill your tokens, select 1 from our product offerings:\n" + \
                                "\n ".join("*{x}*: Buy {y} tokens for {z}{m}".format(x=str(p.index), y=str(p.units), z=str(p.price), m=currency) for p in product_list) + \
                                "\n Or *0*: To go back to main menu"
                            send_text(self.user_num, message, wamid)
                            self.data = WAChatState.Data(product_list=product_list)
                            self.state = WAChatState._CHOOSE_PRODUCT
                        case 4:
                            # selected check payment
                            payments = Payment.objects.filter(user__phone_number=self.user_num).order_by('-created')[:5]
                            message = "Here are the last 5 transactions. Select a transaction to check if there is a status update by sending the number.\n" + \
                                "\n\n".join("*{i}*: {x}{m} via {a}:{n} at {time}. STATUS: {status}".format(i=str(index+1), x=str(p.amount), m=currency, a=p.method, n=p.mobile_wallet_number, time=p.created, status=p.status) for index, p in enumerate(payments)) + \
                                "\n\n To view more transactions go to https://zimgpt.pfitz.co.zw/ or app 263775409679 for help." + \
                                "\n\n Send *0* to go back to menu."
                            send_text(self.user_num, message, wamid)
                            self.state = WAChatState._CHECK_PAYMENT
                        case 5:
                            # selected get free tokens
                            user = get_user_model().objects.get(phone_number=self.user_num)
                            messages = [
                                "*You can get 50,000 tokens which is about 37,500 words!*\n\n For every person you refer you get 50,000 tokens. The person should use the link below to send your ref code, they just follow the link and send the code via whatsapp." + \
                                "\n\n The link is in the message below. Share it and earn more tokens.",
                                "https://wa.me/26777084294?text={code}".format(code=user.profile.ref)
                            ]
                            for message in messages:
                                send_text(self.user_num, message, wamid)
                            self.state = WAChatState._START
                else:
                    # invalid menu selection
                    message = "Sorry. Unfortunately '{x}' is not a valid menu selection.".format(x=input) + WAChatState._menu_text
                    send_text(self.user_num, message, wamid)
                    # state remains the same

            #### case 4: Chat
            case WAChatState._CHAT:
                user = get_user_model().objects.get(phone_number=self.user_num)
                completion = get_chat_completion(user, input, self.data.conv_history)
                if completion.isOkay():
                    # no error
                    self.data.conv_history = completion.response.prompt_history
                    send_text(self.user_num, completion.response.generated_text, wamid)
                else:
                    message = "Error: Ooops, something went wrong!\n\n _Error message: {msg}_".format(msg=completion.error.message)
                    send_text(self.user_num, message, wamid)

            #### case 5: Prompt engineer
            case WAChatState._FREE_PROMPT:
                user = get_user_model().objects.get(phone_number=self.user_num)
                completion = get_completion(user, input)
                if completion.isOkay():
                    # no error
                    send_text(self.user_num, completion.response.generated_text, wamid)
                else:
                    message = "Error: Ooops, something went wrong!\n\n _Error message: {msg}_".format(msg=completion.error.message)
                    send_text(self.user_num, message, wamid)
                pass

            #### case 6: Choose and buy tokens
            case WAChatState._CHOOSE_PRODUCT:
                product_indices = [p.index for p in self.data.product_list]

                # check if any product was selected
                try:

                    if int(input) in product_indices:
                        # pick a product and transition to confirmation state
                        product = [p for p in self.data.product_list if p.index == int(input)][0]
                        self.data.product_id = product.product_id
                        message = "You selected {x} tokens which cost {y}{m}. Send *1* to confirm or *0* to cancel.".format(x=str(product.units), y=str(product.price), m=currency)
                        send_text(self.user_num, message, wamid)
                        self.state = WAChatState._CONFIRM_PRODUCT
                    
                    elif int(input) == 0:
                        # return to main menu
                        self.data = None
                        self.state = WAChatState._MENU
                        message = "Let start again." + WAChatState._menu_text
                        send_text(self.user_num, message, wamid)

                    else:
                        # invalid input
                        message = "Sorry, '{i}' is not a valid selection. Please choose from:\n" + \
                            "\n ".join("*{x}*: Buy {y} tokens for {z}{m}".format(x=str(p.index), y=str(p.units), z=str(p.price), m=currency) for p in self.data.product_list) + \
                            "\n Or *0*: To go back to main menu"
                        send_text(self.user_num, message, wamid)
                        # state remains the same

                except ValueError:
                    # invalid input
                    message = "Sorry, '{i}' is not a valid selection. Please choose from:\n".format(i=input) + \
                        "\n ".join("*{x}*: Buy {y} tokens for {z}{m}".format(x=str(p.index), y=str(p.units), z=str(p.price), m=currency) for p in self.data.product_list) + \
                        "\n Or *0*: To go back to main menu"
                    send_text(self.user_num, message, wamid)
                    # state remains the same

            ### case 7: Receive confirmation or rejection of selected product
            case WAChatState._CONFIRM_PRODUCT:

                if str(input) == '1':
                    # confirmed product selection
                    # ask for payment method
                    message = "How would you like to pay for your product?\n\n Select:\n\n *1* Ecocash\n *2* Telecash\n *3* OneMoney \n *0* To Cancel Payment."
                    send_text(self.user_num, message, wamid)
                    self.state = WAChatState._GET_PAYMENT_METHOD

                elif str(input) == '0':
                    # cancelled selection
                    # offer selection again
                    message = "You can select the product of choice. Please choose from:\n" + \
                        "\n ".join("*{x}*: Buy {y} tokens for {z}{m}".format(x=str(p.index), y=str(p.units), z=str(p.price), m=currency) for p in self.data.product_list) + \
                        "\n Or *0*: To go back to main menu"
                    send_text(self.user_num, message, wamid)

                    self.state = WAChatState._CHOOSE_PRODUCT
                
                else:
                    # invalid input
                    product = [p for p in self.data.product_list if p.product_id == self.product_id][0]
                    message = "Sorry, '{i}' is not a valid response.\n\n You are about to buy {x} tokens which cost {y}{m}. Send *1* to confirm or *0* to cancel.".format(i=input, x=str(product.units), y=str(product.price), m=currency)
                    send_text(self.user_num, message, wamid)
                    # state remains the same

            ### case 8: Select payment method or rejection of selected product    
            case WAChatState._GET_PAYMENT_METHOD:
                
                if str(input) in ['1', '2', '3']:
                    if str(input) == '1':
                        self.data.payment_method = "ecocash"
                    elif str(input) == '2':
                        self.data.payment_method = "telecash"
                    elif str(input) == '3':
                        self.data.payment_method = "onemoney"

                    # ask for mobile wallet number
                    message = "Please provide your mobile wallet number for '{x}' to proceed or enter 0 to cancel payment:".format(x=self.data.payment_method)
                    send_text(self.user_num, message, wamid)
                    self.state = WAChatState._GET_PAYMENT_NUMBER

                elif str(input) == '0':
                    # cancelled
                    message = "You can select the product of choice. Please choose from:\n" + \
                        "\n ".join("*{x}*: Buy {y} tokens for {z}{m}".format(x=p.index, y=p.units, z=p.price, m=currency) for p in self.data.product_list) + \
                        "\n Or *0*: To go back to main menu"
                    send_text(self.user_num, message, wamid)
                    # set state for product selection
                    self.state = WAChatState._CHOOSE_PRODUCT
                
                else:
                    # invalid input
                    message = "Sorry, '{i}' is not a valid response.\n\nHow would you like to pay for your product?\n\n Select:\n\n *1* Ecocash\n *2* Telecash\n *3* OneMoney \n *0* To Cancel Payment.".format(i=input)
                    send_text(self.user_num, message, wamid)
                    #state is not changed

            ### case 9: Get the mobile wallet number
            case WAChatState._GET_PAYMENT_NUMBER:
                
                if re.match(r"^07\d{8}$", input):
                    # matches pattern for Zim mobile numbers
                    self.data.payment_number = input

                    # get product
                    product = [p for p in self.data.product_list if p.product_id == self.product_id][0]

                    # ask for confirmation and email for paynow
                    message = "You are purchasing *{x} tokens* for *{y}{m}* with *'{a}'* number *{n}*.".format(x=product.units, y=product.price, m=currency, a=self.data.payment_method, n=self.data.payment_number) + \
                        "\n\n If information is correct, enter and *send your email address* for payment confirmation." + \
                        "\n\n If incorrect send *0* to cancel payemnt."
                    send_text(self.user_num, message, wamid)
                    self.state = WAChatState._CONFIRM_PAYMENT_DETAILS
                
                elif str(input) == '0':
                    # cancelled
                    message = "You can select the product of choice. Please choose from:\n" + \
                        "\n ".join("*{x}*: Buy {y} tokens for {z}{m}".format(x=p.index, y=p.units, z=p.price, m=currency) for p in self.data.product_list) + \
                        "\n Or *0*: To go back to main menu"
                    send_text(self.user_num, message, wamid)
                    # set state for product selection
                    self.state = WAChatState._CHOOSE_PRODUCT
                
                else:
                    # invalid input
                    message = "Sorry, '{i}' is not a valid response or mobile number.\n\nExample mobile number format is 0777111222\n\n Or *0* To Cancel Payment.".format(i=input)
                    send_text(self.user_num, message, wamid)
                    #state is not changed

            ### case 10: Get confirmation and email as required by paynow
            case WAChatState._CONFIRM_PAYMENT_DETAILS:

                # valid email confirms transaction

                try:
                    validate_email(input)

                    # valid email, process payment
                    response = initiate_payment(
                        get_user_model().objects.get(phone_number=self.user_num),
                        Product.objects.get(uuid=self.data.product_id),
                        self.data.payment_method,
                        self.data.payment_number,
                        input
                    )

                    if response[1] == status.HTTP_200_OK:
                        # payment request accepted
                        message = "Transaction initiated. If you are not automatically prompted to complete payment, follow these instructions:\n\n" + response[0]
                        send_text(self.user_num, message, wamid)
                        self.data = None
                        self.state = WAChatState._START

                    else:
                        # something went wrong
                        # get product
                        product = [p for p in self.data.product_list if p.product_id == self.product_id][0]

                        message = "Sorry, An error occured. Error: {err}.\n\n".format(err=response[0]) + \
                            "You were attempting to purchase *{x} tokens* for *{y}{m}* with *'{a}'* number *{n}*.".format(x=str(product.units), y=str(product.price), m=currency, a=self.data.payment_method, n=self.data.payment_number) + \
                            "\n\n If information is correct, enter and *send your email address* for payment confirmation." + \
                            "\n\n If incorrect send *0* to cancel payemnt."
                        send_text(self.user_num, message, wamid)

                except ValidationError:
                    # not a vaild email
                    if str(input) == '0':
                        # cancelled by user
                        message = "You can select the product of choice. Please choose from:\n" + \
                        "\n ".join("*{x}*: Buy {y} tokens for {z}{m}".format(x=str(p.index), y=str(p.units), z=str(p.price), m=currency) for p in self.data.product_list) + \
                        "\n Or *0*: To go back to main menu"
                        send_text(self.user_num, message, wamid)
                        # set state for product selection
                        self.state = WAChatState._CHOOSE_PRODUCT

                    else:
                        # invalid input
                        # get product
                        product = [p for p in self.data.product_list if p.product_id == self.product_id][0]

                        # ask for confirmation and email for paynow
                        message = "Sorry, '{i}' is neither a valid email nor '0' for cancellation.\n\n".format(i=input) + \
                            "You are purchasing *{x} tokens* for *{y}{m}* with *'{a}'* number *{n}*.".format(x=str(product.units), y=str(product.price), m=currency, a=self.data.payment_method, n=self.data.payment_number) + \
                            "\n\n If information is correct, enter and *send your email address* for payment confirmation." + \
                            "\n\n If incorrect send *0* to cancel payemnt."
                        send_text(self.user_num, message, wamid)
                        # state remains the same


            ### case 11: Check payment status
            case WAChatState._CHECK_PAYMENT:
                if str(input) in ['0', '1', '2', '3', '4', '5']:
                    if str(input) == '0':
                        # return to main menu
                        self.data = None
                        self.state = WAChatState._MENU
                        message = "Let start again." + WAChatState._menu_text
                        send_text(self.user_num, message, wamid)
                    else:
                        # check transaction with matching index
                        payments = Payment.objects.filter(user__phone_number=self.user_num).order_by('-created')[:5]

                        # check if index in range
                        if (len(payments) >= int(input)):
                            # check the payment
                            payment = payments[int(input)-1]
                            check_payment_status(payment)
                            message = "Here is the most current information for the transaction:\n\n" + \
                                "Date and time of payment: {dt}\n".format(dt=str(payment.created)) + \
                                "Amount: {x}{m}\n".format(x=str(payment.amount), m=currency) + "Payment platform: {m}\n".format(m=payment.method) + \
                                "Mobile wallet number: {n}\n".format(n=payment.mobile_wallet_number) + \
                                "Reference: {ref}\n".format(ref=payment.uuid) + "Status: {s}\n".format(s=payment.status) + \
                                "Last updated at: {dt}\n".format(dt=str(payment.updated)) + \
                                "\n\n App 263775409679 for any queries. \n\n Select another transaction or *0* to go back to main menu"
                            send_text(self.user_num, message, wamid)
                            # keep state

                        else:
                            # out of range
                            message = "Sorry, there is no transaction number {i}. Choose a transaction in the list or send *0* to go back to menu.".format(i=input)
                            send_text(self.user_num, message, wamid)
                else:
                    # invalid input
                    message = "Sorry, '{i}' is not a valid response. Choose a transaction or send *0* to go back to menu.".format(i=input)
                    send_text(self.user_num, message, wamid)

            
            ### case 12: This should never occur
            case _:
                message = "Sorry, the system has been reset due to an unknown error. Send any message to start again."
                send_text(self.user_num, message, wamid)
                self.state = WAChatState._START
                self.data = None
        
        return