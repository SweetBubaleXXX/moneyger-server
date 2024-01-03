from decimal import Decimal

from django.forms import ValidationError

from accounts.tests.factories import AccountFactory
from core.constants import CurrencyCode

from ..models import Transaction
from .base import BaseTestCase


class TransactionTests(BaseTestCase):
    def test_amount_decimal(self):
        transaction = self.create_transaction(amount=5000, currency=CurrencyCode.USD)
        self.assertEqual(transaction.amount_decimal, Decimal(50))

    def test_category_different_account(self):
        category = self.create_category()
        with self.assertRaises(ValidationError):
            Transaction.objects.create(
                account=AccountFactory(),
                category=category,
                amount=200,
                currency=CurrencyCode.EUR,
            )
