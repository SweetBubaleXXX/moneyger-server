from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

DEFAULT_CHAT_GROUP = "public_chat"


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.group_name = DEFAULT_CHAT_GROUP
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        user = self.scope["user"]
        if isinstance(user, AnonymousUser):
            return await self.close(code=4004)
        username = await database_sync_to_async(lambda: user.username)()
        is_admin = await database_sync_to_async(lambda: user.is_superuser)()
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "user": username,
                "is_admin": is_admin,
                "message": content["message"],
            },
        )

    async def chat_message(self, event):
        await self.send_json(event)
