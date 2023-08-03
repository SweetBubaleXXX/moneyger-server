from django.urls import reverse
from rest_framework import status

from ...constants import CurrencyChoices, TransactionType
from ..models import Transaction
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
        category = self.create_category()
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


class TransactionDetailsViewTests(BaseTestCase):
    def test_transaction_not_found(self):
        """Response 404 if transaction doesn't exist."""
        response = self.client.get(reverse("transaction-detail", args=(12345,)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_transaction_of_other_account(self):
        """Response 404 when trying to get transaction that belongs to another account."""
        other_account_transaction = self.create_transaction(account=AccountFactory())
        response = self.client.get(
            reverse("transaction-detail", args=(other_account_transaction.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_displays_correct_transaction_type(self):
        """Transaction type in response must be the same in category."""
        transaction = self.create_transaction()
        response = self.client.get(
            reverse("transaction-detail", args=(transaction.id,))
        )
        self.assertEqual(
            response.json()["transaction_type"], transaction.category.transaction_type
        )

    def test_cannot_edit_category(self):
        """Category id in request must be ignored when updating."""
        transaction = self.create_transaction()
        another_category = self.create_category()
        response = self.client.patch(
            reverse("transaction-detail", args=(transaction.id,)),
            {"category": another_category.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.json()["category"], another_category.id)

    def test_updated_transaction(self):
        """Transaction must have provided fields changed."""
        transaction = self.create_transaction()
        request_body = {
            "amount": 555,
            "currency": CurrencyChoices.EUR,
            "comment": "New comment",
        }
        response = self.client.put(
            reverse("transaction-detail", args=(transaction.id,)), request_body
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(request_body.items(), response.json().items())

    def test_delete_transaction(self):
        """Transaction must be successfully deleted."""
        transaction = self.create_transaction()
        response = self.client.delete(
            reverse("transaction-detail", args=(transaction.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(pk=transaction.id)


class CategorizedTransactionViewTests(BaseTestCase):
    def test_transactions_list_amount(self):
        """Response list must contain only transactions of current category."""
        self.create_transactions_batch(10)
        category = self.create_category()
        transactions = self.create_transactions_batch(5, category=category)
        response = self.client.get(
            reverse("transaction-category-transactions", args=(category.id,))
        )
        response_list = response.json()
        self.assertEqual(len(response_list), len(transactions))

    def test_add_transaction_required_fields(self):
        """
        Response an error when trying to create a transaction without necessary fields.
        """
        category = self.create_category()
        response = self.client.post(
            reverse("transaction-category-transactions", args=(category.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("amount", "currency"):
            self.assertListEqual(response.json()[field], ["This field is required."])

    def test_add_transaction_negative_amount(self):
        """Response an error when trying to add a transaction with negative amount."""
        category = self.create_category()
        response = self.client.post(
            reverse("transaction-category-transactions", args=(category.id,)),
            {
                "amount": -100,
                "currency": CurrencyChoices.USD,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_transaction_nonexistent_category(self):
        """Response 404 if trying to add transaction to category that doesn't exist."""
        response = self.client.post(
            reverse("transaction-category-transactions", args=(12345,)),
            {
                "amount": 555,
                "currency": CurrencyChoices.USD,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_transaction_to_other_account(self):
        """Response 404 when trying to add transaction to other account."""
        other_account_category = self.create_category(
            account=AccountFactory(),
        )
        response = self.client.post(
            reverse(
                "transaction-category-transactions", args=(other_account_category.id,)
            ),
            {
                "amount": 555,
                "currency": CurrencyChoices.USD,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_transaction(self):
        """Transaction must be created and have the correct transaction_type."""
        category = self.create_category(
            transaction_type=TransactionType.INCOME,
        )
        request_body = {
            "amount": 555,
            "currency": CurrencyChoices.EUR,
            "comment": "Comment",
        }
        response = self.client.post(
            reverse("transaction-category-transactions", args=(category.id,)),
            request_body,
        )
        expected_response_subdict = request_body | {
            "category": category.id,
            "transaction_type": category.transaction_type,
        }
        self.assertLessEqual(
            expected_response_subdict.items(),
            response.json().items(),
        )
