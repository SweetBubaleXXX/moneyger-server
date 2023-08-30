from collections.abc import Iterable
from typing import Literal, TypedDict

from celery import shared_task, Task
from djoser import email

from .models import Account


class _Context(TypedDict):
    id: int
    domain: str
    protocol: Literal["https", "http"]
    site_name: str


class _SendEmailTask(Task):
    autoretry_for = (Exception,)
    max_retries = 3

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        return super().on_failure(exc, task_id, args, kwargs, einfo)


@shared_task(bind=True, base=_SendEmailTask)
def send_activation_email(self, context: _Context, recipients: Iterable[str]):
    email.ActivationEmail(
        context=context | {"user": Account.objects.get(pk=context["id"])}
    ).send(recipients)
