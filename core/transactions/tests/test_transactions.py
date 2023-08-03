from django.urls import reverse
from rest_framework import status

from .base import BaseTestCase
from .factories import AccountFactory


class TransactionListViewTests(BaseTestCase):
    def test_unauthorized(self):
        """Try to get transactions list without providing authorization credentials."""
        self.client.logout()
        response = self.client.get(reverse("transaction-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_add_transaction(self):
        """Forbid creating transactions using this route."""
        category = self.get_or_create_category()
        response = self.client.post(
            reverse("transaction-list"),
            {
                "category": category.id,
                "amount": 300,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_no_transactions(self):
        """Response must be an empty list if there are on transactions."""
        response = self.client.get(reverse("transaction-list"))
        self.assertListEqual(response.json(), [])

    def test_transactions_list_amount(self):
        """Response list must contain correct amount of items."""
        self.create_transactions_batch(10, AccountFactory())
        own_transactions = self.create_transactions_batch(20)
        response = self.client.get(reverse("transaction-list"))
        response_list = response.json()
        self.assertIsInstance(response_list, list)
        self.assertEqual(len(response_list), len(own_transactions))
