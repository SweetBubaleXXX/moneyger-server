from colorfield.fields import ColorField
from django.conf import settings
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from ..constants import CurrencyChoices, TransactionType


class BaseModel(models.Model):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class TransactionCategory(BaseModel):
    COLOR_PALETTE = [
        ("#ffffff", "white"),
        ("#ff6b22", "orange"),
        ("#cddc39", "lime"),
        ("#b9b9b9", "grey"),
        ("#af2422", "red"),
        ("#673ab7", "purple"),
        ("#4cd964", "green"),
        ("#2196f3", "blue"),
        ("#009688", "dark teal"),
    ]

    parent_category = models.ForeignKey(
        "self",
        related_name="child_categories",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    transaction_type = models.CharField(max_length=3, choices=TransactionType.choices)
    name = models.CharField(max_length=64)
    display_order = models.IntegerField(default=0)
    icon = models.CharField(max_length=64, blank=True)
    color = ColorField(samples=COLOR_PALETTE)


class Transaction(BaseModel):
    category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    amount = models.BigIntegerField()
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)
    comment = models.CharField(max_length=255, blank=True)
    transaction_time = models.DateTimeField(default=timezone.now)
