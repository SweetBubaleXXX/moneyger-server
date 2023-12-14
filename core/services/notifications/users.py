import binascii
import json
from os import urandom
from typing import TYPE_CHECKING, TypedDict

from django.conf import settings

from .producer import Producer

if TYPE_CHECKING:
    from accounts.models import Account


class _AccountCredentials(TypedDict):
    account_id: int
    email: str
    token: str


class UsersProducer(Producer):
    def register_account(self, account: "Account") -> None:
        auth_token = binascii.hexlify(
            urandom(settings.NOTIFICATIONS_SERVICE_TOKEN_LENGTH)
        ).decode()
        credentials = _AccountCredentials(
            account_id=account.id,
            email=account.email,
            token=auth_token,
        )
        self.send("user.event.created", json.dumps(credentials))

    def delete_account(self, account_id: int) -> None:
        self.send("user.event.deleted", account_id)
