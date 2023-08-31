from collections.abc import Iterable, Mapping
from typing import Literal, NotRequired, TypedDict

from celery import shared_task
from djoser import email

from .models import Account

EMAIL_TYPE = Literal[
    "activation",
    "confirmation",
    "password_reset",
    "password_changed_confirmation",
    "username_changed_confirmation",
    "username_reset",
]

_EMAIL_TEMPLATES: Mapping[EMAIL_TYPE, type[email.BaseEmailMessage]] = {
    "activation": email.ActivationEmail,
    "confirmation": email.ConfirmationEmail,
    "password_reset": email.PasswordResetEmail,
    "password_changed_confirmation": email.PasswordChangedConfirmationEmail,
    "username_changed_confirmation": email.UsernameChangedConfirmationEmail,
    "username_reset": email.UsernameResetEmail,
}


class EmailContext(TypedDict):
    type: EMAIL_TYPE
    user_id: int
    domain: str
    protocol: Literal["https", "http"]
    site_name: str
    uid: NotRequired[str]
    token: NotRequired[str]
    url: NotRequired[str]


@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
)
def send_email(context: EmailContext, recipients: Iterable[str]):
    message_class = _EMAIL_TEMPLATES[context["type"]]
    message = message_class(
        context=context | {"user": Account.objects.get(pk=context["user_id"])}
    )
    message.send(recipients)
