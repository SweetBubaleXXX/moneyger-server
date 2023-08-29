from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants import SESSION_TTL_CHOICES, CurrencyCode


class Account(AbstractUser):
    default_currency = models.CharField(
        max_length=3, choices=CurrencyCode.choices, default=CurrencyCode.USD
    )
    session_ttl = models.DurationField(
        choices=SESSION_TTL_CHOICES, default=timedelta(weeks=1)
    )
