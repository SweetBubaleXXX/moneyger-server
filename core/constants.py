from django.db import models
from django.utils.translation import gettext_lazy as _


class CurrencyCode(models.TextChoices):
    USD = "USD"
    EUR = "EUR"
    BYN = "BYN"
    RUB = "RUB"


class TransactionType(models.TextChoices):
    INCOME = "IN", _("Income")
    OUTCOME = "OUT", _("Outcome")
