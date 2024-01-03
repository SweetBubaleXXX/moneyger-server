from django.conf import settings
from django.urls import reverse

from core.services.messages import MessageCache
from core.services.tests.factories import MessageFactory
from core.transactions.tests.base import BaseViewTestCase


class MessagesViewTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.default_message_cache = MessageCache(settings.DEFAULT_CHAT_GROUP)
        self.addCleanup(self.default_message_cache.clear)

    def test_unauthorized(self):
        self._test_get_unauthorized(reverse("chat-messages"))

    def test_no_messages(self):
        response = self.client.get(reverse("chat-messages"))
        self.assertListEqual(response.json(), [])

    def test_messages(self):
        message_count = 20
        for _ in range(message_count):
            self.default_message_cache.push(MessageFactory())
        response = self.client.get(reverse("chat-messages"))
        self.assertEqual(len(response.json()), message_count)
