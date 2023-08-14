from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from .factories import AccountFactory, TransactionCategoryFactory, TransactionFactory


class BaseTestCase(APITestCase):
    def setUp(self):
        self.request_factory = APIRequestFactory()
        self.account = AccountFactory()
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


class BaseViewTestCase(BaseTestCase):
    def _test_list_count(self, path, count):
        response = self.client.get(path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], count)

    def _test_get_unauthorized(self, path):
        self.__test_unauthorized(lambda: self.client.get(path))

    def _test_post_unauthorized(self, path, data):
        self.__test_unauthorized(lambda: self.client.post(path, data))

    def __test_unauthorized(self, request_callback):
        self.client.logout()
        response = request_callback()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
