from collections.abc import Iterable
from typing import Literal, NotRequired, TypedDict

from celery import Task, shared_task
from djoser import email

from .models import Account


class EmailContext(TypedDict):
    user_id: int
    domain: str
    protocol: Literal["https", "http"]
    site_name: str
    uid: NotRequired[str]
    token: NotRequired[str]
    url: NotRequired[str]


class _SendEmailTask(Task):
    autoretry_for = (Exception,)
    max_retries = 3

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        return super().on_failure(exc, task_id, args, kwargs, einfo)

    def _create_message_dispatcher(
        self, message_class: type[email.BaseEmailMessage], context: EmailContext
    ) -> email.BaseEmailMessage:
        return message_class(
            context=context | {"user": Account.objects.get(pk=context["user_id"])}
        )


@shared_task(bind=True, base=_SendEmailTask)
def send_activation_email(
    self: _SendEmailTask, context: EmailContext, recipients: Iterable[str]
):
    self._create_message_dispatcher(email.ActivationEmail, context).send(recipients)
