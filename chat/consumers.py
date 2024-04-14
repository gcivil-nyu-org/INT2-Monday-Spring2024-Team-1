import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from healthScore.models import User
from .models import ChatSession, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = self.scope["url_route"]["kwargs"]["receiver_id"]
        sorted_ids = sorted([int(self.scope["user"].id), int(self.receiver_id)])
        self.room_group_name = f"chat_{sorted_ids[0]}_{sorted_ids[1]}"
        print(self.room_group_name)

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.save_message(self.scope["user"].id, self.receiver_id, message)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "author_id": str(self.scope["user"].id),
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        author_id = event["author_id"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps({"message": message, "author_id": author_id})
        )

    @database_sync_to_async
    def save_message(self, author_id, other_user_id, message):
        author = User.objects.get(id=author_id)
        other_user = User.objects.get(id=other_user_id)

        Msg = Message.objects.create(author=author, content=message)

        chat_session, created = ChatSession.objects.get_or_create(
            patient=author if author.is_patient else other_user,
            healthcareWorker=author if author.is_healthcare_worker else other_user,
        )

        chat_session.messages.add(Msg)
