from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants import CurrencyCode


class Account(AbstractUser):
    default_currency = models.CharField(
        max_length=3, choices=CurrencyCode.choices, default=CurrencyCode.USD
    )
