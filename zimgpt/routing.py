from django.urls import path
from . import consumers

urlpatterns = [
    path('ws/zimgpt/chat/', consumers.ChatCompletionConsumer.as_asgi()),
    path('ws/zimgpt/answer/', consumers.AnswerCompletionConsumer.as_asgi())
]