from django.db import models
from django.contrib.auth import get_user_model
from payments.models import Payment, Product
import uuid

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    tokens_remaining = models.IntegerField(default=0)
    chat_max_tokens = models.IntegerField(default=4000)
    wa_chat_state = models.JSONField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    ref = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.user.phone_number

class APIRequest(models.Model):
    SERVICE_CHAT = "CHAT"
    SERVICE_ANSWERS = "ANS"
    service_choices = [
        (SERVICE_CHAT, "CHAT"),
        (SERVICE_ANSWERS, "ANSWERS"),
    ]
    service= models.CharField(max_length=50, choices=service_choices)
    prompt = models.TextField()
    prompt_tokens = models.IntegerField()
    tokens_used = models.IntegerField()
    tokens_remaining = models.IntegerField()
    ai_model = models.CharField(max_length=256)
    response_text = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class TokenReload(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    payment = models.OneToOneField(Payment, on_delete=models.RESTRICT)
    loaded = models.BooleanField(default=False)
    load_timestamp = models.DateTimeField(default=None, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


# Other objects
class ClientCompletionResponse:
    ERROR_ACCESS_VALIDATION = "ACCESS_VALIDATION"
    ERROR_API_ERROR = "UPSTREAM_API"
    ERROR_INTERNAL_SERVER = "INTERNAL_SERVER_ERROR"

    class Response:
        def __init__ (self, generated_text, prompt_tokens, used_tokens, prompt_history):
            self.generated_text = generated_text
            self.prompt_tokens = prompt_tokens
            self.used_tokens = used_tokens
            self.prompt_history = prompt_history

    class Error:
        def __init__(self, source, message):
            self.source = source
            self.message = message

    def __init__ (self, response, error):
        self.response = response
        self.error = error

    def isOkay(self) -> bool:
        return True if isinstance(self.response, self.Response) else False

class UpstreamCompletionResponse:
    class Choice:
        def __init__(self, text=None, index=None, logprobs=None, finish_reason=None):
            self.text = text
            self.index = index
            self.logprobs = logprobs
            self.finish_reason = finish_reason

    class Usage:
        def __init__(self, prompt_tokens, completion_tokens, total_tokens):
            self.prompt_tokens = prompt_tokens
            self.completion_tokens = completion_tokens
            self.total_tokens = total_tokens
    
    def __init__(self, id, object, created, model, choices, usage):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = choices
        self.usage = usage

class UpstreamChatCompletionResponse:
    class Choice:
        def __init__(self, delta=None, message=None, index=None, finish_reason=None):
            self.message = message
            self.delta = delta
            self.index = index
            self.finish_reason = finish_reason
        
        class Message:
            def __init__(self, role=None, content=None):
                self.role = role
                self.content = content

            def __str__(self) -> str:
                return "Message(role='{role}', content='{content}')".format(role=self.role, content=self.content)
        
        class Delta:
            def __init__(self, role=None, content=None):
                self.role = role
                self.content = content
            
            def __str__(self) -> str:
                return "Delta(role='{role}', content='{content}')".format(role=self.role, content=self.content)

    class Usage:
        def __init__(self, prompt_tokens, completion_tokens, total_tokens):
            self.prompt_tokens = prompt_tokens
            self.completion_tokens = completion_tokens
            self.total_tokens = total_tokens
    
    def __init__(self, id, object, created, model, choices, usage=None):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = choices
        self.usage = usage
