from datetime import datetime
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from chatinterface.models import ChatMessage
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "lobby"
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        self.user_id = self.scope["user"].id
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
                "author": self.scope["user"].username,
                "created_at": chat_message.created_at.strftime("%b. %d, %Y, %I:%M %p").replace("AM", "a.m.").replace("PM", "p.m."),
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        message_data = {
            "content": event["message"],
            "author": event["author"],
            "created_at": event["created_at"],
        }
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message_data))

    @database_sync_to_async
    def persist_message(self, content) -> ChatMessage:
        message = ChatMessage(
            author=User.objects.get(id=self.user_id), content=content, created_at=datetime.now()
        )
        message.save()

        return message
