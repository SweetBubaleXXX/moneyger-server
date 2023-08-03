from django.test import TestCase
from rest_framework.test import APIClient

from .factories import AccountFactory, TransactionCategoryFactory, TransactionFactory


class BaseTestCase(TestCase):
    def setUp(self):
        self.account = AccountFactory()
        self.client = APIClient()
        self.client.force_login(self.account)

    def get_or_create_category(self, account=None, parent_category=None, **kwargs):
        return TransactionCategoryFactory(
            account=account or self.account, parent_category=parent_category, **kwargs
        )

    def get_or_create_transaction(self, account=None, category=None, **kwargs):
        account = account or self.account
        return TransactionFactory(
            account=account,
            category=category or self.get_or_create_category(account=account),
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
        return TransactionFactory.create_batch(
            size,
            account=account,
            category=category or self.get_or_create_category(account=account),
            **kwargs
        )
