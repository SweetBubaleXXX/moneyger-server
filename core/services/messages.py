from collections import deque
from typing import TypedDict

from django.conf import settings
from django.core.cache import caches

_DEFAULT_CACHE_NAME = "default"


class SerializedMessage(TypedDict):
    message_id: str
    user: str
    is_admin: bool
    message_text: str
    timestamp: float


class MessageCache:
    def __init__(self, group_name: str, cache_name: str = _DEFAULT_CACHE_NAME):
        self._cache_key = f"{group_name}_messages"
        self._cache = caches[cache_name]

    def get_all(self) -> deque[SerializedMessage]:
        recent_messages = self._cache.get(
            self._cache_key, deque(maxlen=settings.CHAT_CACHE_SIZE_LIMIT)
        )
        return recent_messages

    def push(self, message: SerializedMessage) -> SerializedMessage:
        recent_messages: deque = self._cache.get_or_set(
            self._cache_key,
            deque(maxlen=settings.CHAT_CACHE_SIZE_LIMIT),
            timeout=None,
        )
        recent_messages.append(message)
        self._cache.set(self._cache_key, recent_messages, timeout=None)
        return message

    def clear(self):
        self._cache.delete(self._cache_key)
