from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from .tasks import get_chat_completion_streamed, get_answer_completion_streamed
import json

import logging

logger = logging.getLogger(__name__)

class ChatCompletionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug("ChatCompletion Websocket connected")
        await self.channel_layer.group_add(self.scope["user"].phone_number, self.channel_name)
        await self.accept()
    
    async def receive(self, text_data=None, bytes_data=None):
        logger.debug("ChatCompletion Websocket received data: %s", text_data)
        data = json.loads(text_data)
        get_chat_completion_streamed.delay(self.scope["user"].phone_number, data.get("prompt_text", None), data.get("messages", None))
    
    async def chat_completion(self, event):
        logger.debug("ChatCompletion Websocket received channel data: %s", event["data"])
        await self.send(event["data"])
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.scope["user"].phone_number, self.channel_name)
        return super().disconnect(code)
    
class AnswerCompletionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug("AnswerCompletion Websocket connected")
        await self.channel_layer.group_add(self.scope["user"].phone_number, self.channel_name)
        await self.accept()
    
    async def receive(self, text_data=None, bytes_data=None):
        logger.debug("AnswerCompletion Websocket received data: %s", text_data)
        data = json.loads(text_data)
        get_answer_completion_streamed.delay(self.scope["user"].phone_number, data.get("question", None), data.get("citations", None), data.get("words", None))
    
    async def answer_completion(self, event):
        logger.debug("AnswerCompletion Websocket received channel data: %s", event["data"])
        await self.send(event["data"])
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.scope["user"].phone_number, self.channel_name)
        return super().disconnect(code)