from collections import deque

from django.conf import settings
from django.test import TestCase

from core.services.messages import MessageCache
from core.tests import CacheClearMixin

from .factories import MessageFactory


class TestMessageCache(CacheClearMixin, TestCase):
    def test_empty_cache(self):
        message_cache = self._get_cache()
        messages = message_cache.get_all()
        self.assertIsInstance(messages, deque)
        self.assertEqual(len(messages), 0)

    def test_push_message(self):
        message_cache = self._get_cache()
        message_cache.push(MessageFactory())
        messages = message_cache.get_all()
        self.assertEqual(len(messages), 1)
        self.assertIsInstance(messages[0], dict)

    def test_cache_size_limit(self):
        message_cache = self._get_cache()
        for _ in range(settings.CHAT_CACHE_SIZE_LIMIT + 20):
            message_cache.push(MessageFactory())
        messages = message_cache.get_all()
        self.assertEqual(len(messages), settings.CHAT_CACHE_SIZE_LIMIT)

    def test_clear(self):
        message_cache = self._get_cache()
        message_cache.push(MessageFactory())
        message_cache.clear()
        messages = message_cache.get_all()
        self.assertEqual(len(messages), 0)

    def _get_cache(self):
        return MessageCache("default_group")
