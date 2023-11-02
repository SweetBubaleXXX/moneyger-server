from uuid import uuid4

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from .services import MessageCache, SerializedMessage


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.group_name = settings.DEFAULT_CHAT_GROUP
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        user = self.scope["user"]
        if isinstance(user, AnonymousUser):
            return await self.close(code=4004)
        if "message" not in content:
            return
        username = await database_sync_to_async(lambda: user.username)()
        is_admin = await database_sync_to_async(lambda: user.is_superuser)()
        message = SerializedMessage(
            message_id=str(uuid4()),
            user=username,
            is_admin=is_admin,
            message_text=content["message"],
            timestamp=timezone.now().timestamp(),
        )
        MessageCache(self.group_name).push(message)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                **message,
            },
        )

    async def chat_message(self, event):
        await self.send_json(event)
