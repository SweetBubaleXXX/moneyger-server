from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import (
    DEFAULT_ACCOUNT_PASSWORD,
    AccountFactory,
    TransactionCategoryFactory,
)
from ..constants import TransactionType


class TransactionCategoryViewTests(TestCase):
    def setUp(self):
        self.account = AccountFactory()
        self.client = APIClient()
        self.client.login(
            username=self.account.username, password=DEFAULT_ACCOUNT_PASSWORD
        )

    def test_unauthorized(self):
        """Try to get categories list without providing authorization credentials."""
        self.client.logout()
        response = self.client.get(reverse("transaction-category-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_categories(self):
        """Response should be an empty list if there are on categories."""
        response = self.client.get(reverse("transaction-category-list"))
        self.assertListEqual(response.json(), [])

    def test_categories_list_amount(self):
        """Response list should contain correct amount of items."""
        categories_amount = 5
        TransactionCategoryFactory.create_batch(
            categories_amount,
            account=self.account,
            parent_category=None,
        )
        response = self.client.get(reverse("transaction-category-list"))
        response_list = response.json()
        self.assertIsInstance(response_list, list)
        self.assertEqual(len(response_list), categories_amount)

    def test_add_subcategory(self):
        """Subcategory should be created and have the same transaction_type."""
        parent_category = TransactionCategoryFactory(
            account=self.account,
            parent_category=None,
            transaction_type=TransactionType.INCOME[0],
        )
        response = self.client.post(
            reverse("transaction-category-subcategories", args=(parent_category.id,)),
            {"name": "Subcategory"},
        )
        self.assertDictContainsSubset(
            {
                "parent_category": parent_category.id,
                "transaction_type": parent_category.transaction_type,
                "name": "Subcategory",
            },
            response.json(),
        )
