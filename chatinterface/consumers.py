from datetime import datetime
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chatinterface.models import ChatMessage

from django.core import serializers


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "lobby"
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]
        print("self.user", self.user)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # perist messages to DB
        chat_message: ChatMessage = await self.persist_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": chat_message.content,
                "author": chat_message.author,
                "create_at": chat_message.created_at,
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def persist_message(self, content) -> ChatMessage:
        message = ChatMessage(
            author=self.user, content=content, created_at=datetime.now()
        )
        message.save()

        return message
