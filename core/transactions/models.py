from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import ValidationError
from django.utils import timezone
from simple_history.models import HistoricalRecords

from ..constants import CurrencyCode, TransactionType
from ..services import currency


class BaseModel(models.Model):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class TransactionCategory(BaseModel):
    parent_category = models.ForeignKey(
        "self",
        related_name="subcategories",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    transaction_type = models.CharField(max_length=3, choices=TransactionType.choices)
    name = models.CharField(max_length=64)
    display_order = models.IntegerField(default=0)
    icon = models.CharField(max_length=64, blank=True)
    color = ColorField()

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Transaction(BaseModel):
    category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    amount = models.BigIntegerField(validators=(MinValueValidator(1),))
    currency = models.CharField(max_length=3, choices=CurrencyCode.choices)
    comment = models.CharField(max_length=255, blank=True)
    transaction_time = models.DateTimeField(
        default=timezone.now, validators=(MaxValueValidator(timezone.now),)
    )

    @property
    def amount_decimal(self):
        return currency.int_to_decimal(self.amount, self.currency)

    @amount_decimal.setter
    def amount_decimal(self, value):
        self.amount = currency.decimal_to_int(value, self.currency)

    def clean(self):
        super().clean()
        if self.account != self.category.account:
            raise ValidationError("Category must have the same account.")

    def __str__(self):
        return f"{self.category} [{self.id}]"


@receiver(pre_save, sender=Transaction)
def validate_transaction(sender, instance, raw, **kwargs):
    if not raw:
        instance.full_clean()
