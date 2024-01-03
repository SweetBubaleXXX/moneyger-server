import jwt
from django.utils import timezone
from rest_framework_simplejwt.settings import api_settings as jwt_settings

from core.services.notifications.users import UsersProducer, UsersRpcService
from moneymanager import services_container

from .models import Account


@services_container.inject("users_producer")
def unsubscribe_user_from_notifications(
    account: Account,
    users_producer: UsersProducer,
) -> None:
    users_producer.delete_account(account.id).send()


@services_container.inject("users_rpc_service")
def get_notifications_service_secret(
    account_id: int, users_rpc_service: UsersRpcService
) -> str:
    credentials = users_rpc_service.get_account_credentials(account_id)
    return credentials.token


def create_notifications_service_token(account_id: int) -> str:
    token_secret = get_notifications_service_secret(account_id)
    token_issue_time = timezone.now()
    token_expiration_time = token_issue_time + jwt_settings.ACCESS_TOKEN_LIFETIME
    access_token = jwt.encode(
        {
            "account_id": account_id,
            "iat": token_issue_time.timestamp(),
            "exp": token_expiration_time.timestamp(),
        },
        token_secret,
    )
    return access_token
