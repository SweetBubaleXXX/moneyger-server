from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import AccountFactory, TransactionCategoryFactory, DEFAULT_ACCOUNT_PASSWORD


class TransactionCategoryViewTests(TestCase):
    def setUp(self):
        self.account = AccountFactory()
        self.client = APIClient()
        self.client.login(
            username=self.account.username, password=DEFAULT_ACCOUNT_PASSWORD
        )

    def test_unauthorized(self):
        self.client.logout()
        response = self.client.get(reverse("transaction-category-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_list(self):
        response = self.client.get(reverse("transaction-category-list"))
        self.assertListEqual(response.json(), [])
