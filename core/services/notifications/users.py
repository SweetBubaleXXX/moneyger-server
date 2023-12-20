import binascii
import json
from dataclasses import asdict, dataclass
from os import urandom
from typing import TYPE_CHECKING, Self

from django.conf import settings

from core.services.notifications.rpc import RpcService

from .producer import Producer
from .publishers import PublisherMessage

if TYPE_CHECKING:
    from accounts.models import Account


@dataclass
class AccountCredentials:
    account_id: int
    email: str
    token: str


class UsersProducer(Producer):
    def register_account(self, account: "Account") -> Self:
        auth_token = binascii.hexlify(
            urandom(settings.NOTIFICATIONS_SERVICE_TOKEN_LENGTH)
        ).decode()
        credentials = AccountCredentials(
            account_id=account.id,
            email=account.email,
            token=auth_token,
        )
        self.publisher.add_message(
            PublisherMessage(
                routing_key="user.event.created",
                body=json.dumps(asdict(credentials)),
            )
        )
        return self

    def delete_account(self, account_id: int) -> Self:
        self.publisher.add_message(
            PublisherMessage(
                routing_key="user.event.deleted",
                body=account_id,
            )
        )
        return self


class UsersRpcService(RpcService):
    def get_account_credentials(self, account_id: int) -> AccountCredentials:
        with self.client.connection() as connection:
            response = connection.call(
                PublisherMessage(
                    routing_key="user.request.credentials",
                    body=str(account_id),
                )
            )
            return self._parse_credentials_response(response)

    def _parse_credentials_response(self, response: bytes) -> AccountCredentials:
        deserialized_response = json.loads(response)
        success = deserialized_response.get("success", False)
        if not success:
            raise Exception("Unsuccessful RPC call result")
        result = deserialized_response.get("result")
        return AccountCredentials(**result)
