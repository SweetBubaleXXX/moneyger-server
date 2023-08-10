from decimal import Decimal
from unittest.mock import MagicMock

from django.test import TestCase
from rest_framework.test import APIClient

from moneymanager import services_container

from ...constants import TransactionType
from ..services import CurrencyConverter
from .factories import AccountFactory, TransactionCategoryFactory, TransactionFactory


class BaseTestCase(TestCase):
    def setUp(self):
        self.account = AccountFactory()
        self.client = APIClient()
        self.client.force_login(self.account)

    def create_category(self, account=None, parent_category=None, **kwargs):
        return TransactionCategoryFactory(
            account=account or self.account, parent_category=parent_category, **kwargs
        )

    def create_transaction(self, account=None, category=None, **kwargs):
        account = account or self.account
        return TransactionFactory(
            account=account,
            category=category or self.create_category(account=account),
            **kwargs
        )

    def create_categories_batch(
        self, size, account=None, parent_category=None, **kwargs
    ):
        return TransactionCategoryFactory.create_batch(
            size,
            account=account or self.account,
            parent_category=parent_category,
            **kwargs
        )

    def create_transactions_batch(self, size, account=None, category=None, **kwargs):
        account = account or self.account
        category = category or self.create_category(account=account)
        return TransactionFactory.create_batch(
            size, account=account, category=category, **kwargs
        )


class IncomeOutcomeCategoriesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.income_category = self.create_category(
            transaction_type=TransactionType.INCOME
        )
        self.outcome_category = self.create_category(
            transaction_type=TransactionType.OUTCOME
        )


class MockCurrencyConvertorMixin(TestCase):
    CONVERTION_RATE = Decimal(2)

    def setUp(self):
        super().setUp()
        self.converter_mock = MagicMock(CurrencyConverter)
        self.converter_mock.convert.side_effect = (
            lambda amount, *_: amount * self.CONVERTION_RATE
        )
        services_container.currency_converter.override(self.converter_mock)
