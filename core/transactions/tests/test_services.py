from decimal import Decimal
from unittest.mock import MagicMock

from ...constants import CurrencyCode, TransactionType
from ...services.currency import CurrencyConverter
from ..services import compute_total
from .base import BaseTestCase


class ComputeTotalTestCase(BaseTestCase):
    CONVERTION_RATE = Decimal(2)

    def setUp(self):
        super().setUp()
        self.converter_mock = MagicMock(CurrencyConverter)
        self.converter_mock.convert.side_effect = (
            lambda amount, *_: amount * self.CONVERTION_RATE
        )
        self.income_category = self.create_category(
            transaction_type=TransactionType.INCOME
        )
        self.outcome_category = self.create_category(
            transaction_type=TransactionType.OUTCOME
        )

    def test_no_transactions(self):
        """Must return 0 if there are no transactions."""
        total = compute_total([], CurrencyCode.RUB, self.converter_mock)
        self.assertEqual(total, Decimal(0))

    def test_income_no_convertion(self):
        """Must return correct positive value."""
        transactions = self.create_transactions_batch(
            30, category=self.income_category, amount=200, currency=CurrencyCode.USD
        )
        total = compute_total(transactions, CurrencyCode.USD, self.converter_mock)
        self.assertEqual(total, Decimal(60))

    def test_outcome_no_convertion(self):
        """Must return correct negative value."""
        transactions = self.create_transactions_batch(
            50, category=self.outcome_category, amount=300, currency=CurrencyCode.EUR
        )
        total = compute_total(transactions, CurrencyCode.EUR, self.converter_mock)
        self.assertEqual(total, Decimal(-150))

    def test_income_and_outcome_no_convertion(self):
        """Must treat income as positive value and outcome as negative."""
        income_transactions = self.create_transactions_batch(
            30, category=self.income_category, amount=200, currency=CurrencyCode.BYN
        )
        outcome_transactions = self.create_transactions_batch(
            50, category=self.outcome_category, amount=300, currency=CurrencyCode.BYN
        )
        total = compute_total(
            income_transactions + outcome_transactions,
            CurrencyCode.BYN,
            self.converter_mock,
        )
        self.assertEqual(total, Decimal(-90))

    def test_convertion_called(self):
        """Must convert currencies if output currency is different."""
        transactions = self.create_transactions_batch(
            10, category=self.income_category, amount=10, currency=CurrencyCode.USD
        )
        compute_total(transactions, CurrencyCode.BYN, self.converter_mock)
        self.converter_mock.convert.assert_called_with(
            Decimal("0.1"), CurrencyCode.USD, CurrencyCode.BYN
        )

    def test_convertion_multiple_currencies(self):
        """Must return correct total of transactions with different currencies."""
        usd_transactions = self.create_transactions_batch(
            10, category=self.income_category, amount=500, currency=CurrencyCode.USD
        )
        byn_transactions = self.create_transactions_batch(
            5, category=self.income_category, amount=2000, currency=CurrencyCode.BYN
        )
        total = compute_total(
            usd_transactions + byn_transactions, CurrencyCode.BYN, self.converter_mock
        )
        self.assertEqual(total, Decimal("50") * self.CONVERTION_RATE + Decimal("100"))
