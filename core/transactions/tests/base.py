from decimal import Decimal
from unittest.mock import MagicMock

from django.test import TestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from moneymanager import services_container

from ...constants import TransactionType
from ..services import CurrencyConverter
from .factories import AccountFactory, TransactionCategoryFactory, TransactionFactory


class BaseTestCase(APITestCase):
    def setUp(self):
        self.account = AccountFactory()

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
        if parent_category:
            kwargs["transaction_type"] = parent_category.transaction_type
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


class BaseViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = APIRequestFactory()
        self.client.force_login(self.account)

    def _test_list_count(self, path, count):
        response = self.client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], count)

    def _test_get_queries_number(self, num, path, **kwargs):
        with self.assertNumQueries(num):
            request = self.request_factory.get(path)
            self.__call_view(path, request, **kwargs)

    def _test_post_queries_number(self, num, path, data, **kwargs):
        with self.assertNumQueries(num):
            request = self.request_factory.post(path, data)
            self.__call_view(path, request, **kwargs)

    def __call_view(self, path, request, **kwargs):
        force_authenticate(request, self.account)
        view = resolve(path).func
        view(request, **kwargs)

    def _test_get_unauthorized(self, path):
        self.__test_unauthorized(lambda: self.client.get(path))

    def _test_post_unauthorized(self, path, data):
        self.__test_unauthorized(lambda: self.client.post(path, data))

    def __test_unauthorized(self, request_callback):
        self.client.logout()
        response = request_callback()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MockCurrencyConvertorMixin(TestCase):
    CONVERTION_RATE = Decimal(2)

    def setUp(self):
        super().setUp()
        self.converter_mock = MagicMock(CurrencyConverter)
        self.converter_mock.convert.side_effect = (
            lambda amount, *_: amount * self.CONVERTION_RATE
        )
        services_container.currency_converter.override(self.converter_mock)
