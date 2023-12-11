import binascii
import json
from os import urandom
from typing import TypedDict

from django.conf import settings
from django.contrib.auth.models import User

from .producer import Producer


class _UserCredentials(TypedDict):
    account_id: int
    email: str
    token: str


class UserCreatedProducer(Producer):
    def _publish(self, message: User) -> None:
        auth_token = binascii.hexlify(
            urandom(settings.NOTIFICATIONS_SERVICE_TOKEN_LENGTH)
        ).decode()
        credentials = _UserCredentials(
            account_id=message.account_id,
            email=message.email,
            token=auth_token,
        )
        self.channel.basic_publish(
            self.exchange.name,
            routing_key="user.event.created",
            body=json.dumps(credentials),
        )


class UserDeletedProducer(Producer):
    def _publish(self, message: int) -> None:
        self.channel.basic_publish(
            self.exchange.name,
            routing_key="user.event.deleted",
            body=message,
        )
