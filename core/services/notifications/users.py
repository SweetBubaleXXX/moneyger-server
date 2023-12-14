import binascii
import json
from os import urandom
from typing import TYPE_CHECKING, Self, TypedDict

from django.conf import settings

from .producer import Producer
from .publishers import Message

if TYPE_CHECKING:
    from accounts.models import Account


class _AccountCredentials(TypedDict):
    account_id: int
    email: str
    token: str


class UsersProducer(Producer):
    def register_account(self, account: "Account") -> Self:
        auth_token = binascii.hexlify(
            urandom(settings.NOTIFICATIONS_SERVICE_TOKEN_LENGTH)
        ).decode()
        credentials = _AccountCredentials(
            account_id=account.id,
            email=account.email,
            token=auth_token,
        )
        self.publisher.add_message(
            Message(
                routing_key="user.event.created",
                body=json.dumps(credentials),
            )
        )
        return self

    def delete_account(self, account_id: int) -> Self:
        self.publisher.add_message(
            Message(
                routing_key="user.event.deleted",
                body=account_id,
            )
        )
        return self
