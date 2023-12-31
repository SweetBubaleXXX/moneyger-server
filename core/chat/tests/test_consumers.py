from contextlib import asynccontextmanager

from asgiref.sync import sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from django.urls import path
from rest_framework_simplejwt.tokens import AccessToken

from accounts.tests.factories import AccountFactory
from core.tests import MockPublishersMixin

from ..consumers import ChatConsumer
from ..middleware import JWTAuthMiddleware


class ChatConsumerTests(MockPublishersMixin, TransactionTestCase):
    def setUp(self):
        super().setUp()
        self.user = AccountFactory()
        self.access_token = str(AccessToken.for_user(self.user))
        self.application = JWTAuthMiddleware(
            URLRouter([path("", ChatConsumer.as_asgi())])
        )

    async def test_connection(self):
        async with self._connect(self.access_token):
            pass

    async def test_unauthorized(self):
        async with self._connect():
            await self._test_receive_failed()

    async def test_invalid_token(self):
        async with self._connect("invalid_token"):
            await self._test_receive_failed()

    async def test_message(self):
        async with self._connect(self.access_token):
            await self.communicator.send_json_to({"message": "Test message"})
            response = await self.communicator.receive_json_from()
            self.assertEqual(
                response,
                response
                | {
                    "type": "chat.message",
                    "user": self.user.username,
                    "is_admin": False,
                    "message_text": "Test message",
                },
            )

    async def test_message_notification(self):
        async with self._connect(self.access_token):
            await self.communicator.send_json_to({"message": "Test message"})
            await self.communicator.receive_json_from()
            self.publisher_mock.add_message.assert_called_once()
            self.publisher_mock.publish.assert_called_once()

    async def test_admin(self):
        self.user.is_superuser = True
        await sync_to_async(self.user.save)()
        async with self._connect(self.access_token):
            await self.communicator.send_json_to({"message": "Test message"})
            response = await self.communicator.receive_json_from()
            self.assertTrue(response["is_admin"])

    async def _test_receive_failed(self):
        with self.assertRaises(AssertionError):
            await self.communicator.receive_from()

    @asynccontextmanager
    async def _connect(self, access_token: str | None = None):
        if access_token:
            url = f"/?token={access_token}"
        else:
            url = "/"
        self.communicator = WebsocketCommunicator(self.application, url)
        try:
            connected, _ = await self.communicator.connect()
            self.assertTrue(connected)
            yield
        finally:
            await self.communicator.disconnect()
