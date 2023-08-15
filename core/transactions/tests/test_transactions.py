from datetime import timedelta
from urllib.parse import quote

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from ...constants import CurrencyCode, TransactionType
from ..models import Transaction
from .base import (
    IncomeOutcomeCategoriesTestCase,
    MockCurrencyConvertorMixin,
)
from .base import BaseViewTestCase
from .factories import AccountFactory


class TransactionListViewTests(BaseViewTestCase):
    def test_list_transactions_unauthorized(self):
        """Try to get transactions list without providing authorization credentials."""
        self._test_get_unauthorized(reverse("transaction-list"))

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
        """Response must be empty if there are on transactions."""
        self._test_list_count(reverse("transaction-list"), 0)

    def test_transactions_list_amount(self):
        """Response must contain correct amount of items."""
        self.create_transactions_batch(10, AccountFactory())
        own_transactions = self.create_transactions_batch(20)
        self._test_list_count(reverse("transaction-list"), len(own_transactions))

    def test_list_queries_number(self):
        """Exactly 1 query must be performed."""
        self._test_get_queries_number(1, reverse("transaction-list"))


class TransactionDetailsViewTests(BaseViewTestCase):
    def test_transaction_not_found(self):
        """Response 404 if transaction doesn't exist."""
        response = self.client.get(reverse("transaction-detail", args=(12345,)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_transaction_of_other_account(self):
        """
        Response 404 when trying to get transaction that belongs to another account.
        """
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

    def test_set_nonexistent_category(self):
        """Response an error if trying to set a category that doesn't exist."""
        transaction = self.create_transaction()
        response = self.client.patch(
            reverse("transaction-detail", args=(transaction.id,)),
            {"category": 12345},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(response.json()["category"], ["Invalid category id."])

    def test_set_category_of_other_account(self):
        """
        Response an error if trying to set a category that belongs to another account.
        """
        transaction = self.create_transaction()
        other_account_category = self.create_category(account=AccountFactory())
        response = self.client.patch(
            reverse("transaction-detail", args=(transaction.id,)),
            {"category": other_account_category.id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(response.json()["category"], ["Invalid category id."])

    def test_set_category_of_other_account(self):
        """Transaction category must be successfully changed."""
        transaction = self.create_transaction()
        another_category = self.create_category()
        response = self.client.patch(
            reverse("transaction-detail", args=(transaction.id,)),
            {"category": another_category.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["category"], another_category.id)

    def test_updated_transaction(self):
        """Transaction must have provided fields changed."""
        transaction = self.create_transaction()
        request_body = {
            "amount": "123.45",
            "currency": CurrencyCode.EUR,
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


class CategorizedTransactionViewTests(
    IncomeOutcomeCategoriesTestCase, BaseViewTestCase
):
    def test_list_transactions(self):
        """Response must contain only transactions of current category."""
        self.create_transactions_batch(10)
        category = self.create_category()
        transactions = self.create_transactions_batch(5, category=category)
        self._test_list_count(
            reverse("transaction-category-transactions", args=(category.id,)),
            len(transactions),
        )

    def test_list_queries_number(self):
        """Exactly 3 queries must be performed."""
        category = self.create_category()
        self._test_get_queries_number(
            3,
            reverse("transaction-category-transactions", args=(category.id,)),
            category_id=category.id,
        )

    def test_list_transactions_recursive(self):
        """Response must contain transactions of subcategories."""
        subcategories = self.create_categories_batch(
            30, parent_category=self.outcome_category
        )
        for category in subcategories:
            self.create_transactions_batch(5, category=category)
        self._test_list_count(
            reverse(
                "transaction-category-transactions", args=(self.outcome_category.id,)
            ),
            150,
        )

    def test_add_transaction_required_fields(self):
        """
        Response an error when trying to create a transaction without necessary fields.
        """
        response = self.client.post(
            reverse(
                "transaction-category-transactions", args=(self.outcome_category.id,)
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("amount", "currency"):
            self.assertListEqual(response.json()[field], ["This field is required."])

    def test_add_transaction_negative_amount(self):
        """Response an error when trying to add a transaction with negative amount."""
        response = self.client.post(
            reverse(
                "transaction-category-transactions", args=(self.outcome_category.id,)
            ),
            {
                "amount": -100,
                "currency": CurrencyCode.USD,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_transaction_zero_amount(self):
        """Response an error when trying to add a transaction with zero amount."""
        response = self.client.post(
            reverse(
                "transaction-category-transactions", args=(self.outcome_category.id,)
            ),
            {
                "amount": 0,
                "currency": CurrencyCode.USD,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_future_transaction(self):
        """Disallow adding transactions with future transaction time."""
        response = self.client.post(
            reverse(
                "transaction-category-transactions", args=(self.outcome_category.id,)
            ),
            {
                "amount": 555,
                "currency": CurrencyCode.USD,
                "transaction_time": timezone.now() + timedelta(days=7),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_transaction_nonexistent_category(self):
        """Response 404 if trying to add transaction to category that doesn't exist."""
        response = self.client.post(
            reverse("transaction-category-transactions", args=(12345,)),
            {
                "amount": 555,
                "currency": CurrencyCode.USD,
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
                "currency": CurrencyCode.USD,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_transaction(self):
        """Transaction must be created and have the correct transaction_type."""
        request_body = {
            "amount": "123.45",
            "currency": CurrencyCode.EUR,
            "comment": "Comment",
        }
        response = self.client.post(
            reverse(
                "transaction-category-transactions", args=(self.income_category.id,)
            ),
            request_body,
        )
        expected_response_subdict = request_body | {
            "category": self.income_category.id,
            "transaction_type": TransactionType.INCOME,
        }
        self.assertLessEqual(
            expected_response_subdict.items(),
            response.json().items(),
        )

    def test_add_transaction_queries_number(self):
        """Exactly 3 queries must be performed."""
        category = self.create_category()
        self._test_post_queries_number(
            3,
            reverse("transaction-category-transactions", args=(category.id,)),
            data={
                "category": category.id,
                "amount": "1.23",
                "currency": CurrencyCode.BYN,
            },
            category_id=category.id,
        )


class TransactionSummaryViewTests(
    MockCurrencyConvertorMixin, IncomeOutcomeCategoriesTestCase, BaseViewTestCase
):
    def test_unauthorized(self):
        """Try to get summary without providing authorization credentials."""
        self._test_get_unauthorized(reverse("transaction-summary"))

    def test_no_transactions(self):
        """Total value in response must be 0 if there are no transactions."""
        response = self.client.get(reverse("transaction-summary"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["total"], 0)

    def test_currency(self):
        """Must use account's default currency."""
        response = self.client.get(reverse("transaction-summary"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["currency"], self.account.default_currency)

    def test_filter_outcome(self):
        """Total value must be negative."""
        self.create_transactions_batch(10, category=self.income_category, amount=100)
        self.create_transactions_batch(5, category=self.outcome_category, amount=100)
        response = self.client.get(
            "{}?transaction_type={}".format(
                reverse("transaction-summary"), TransactionType.OUTCOME
            )
        )
        self.assertGreater(0, response.json()["total"])

    def test_filter_income(self):
        """Total value must be positive."""
        self.create_transactions_batch(5, category=self.income_category, amount=100)
        self.create_transactions_batch(10, category=self.outcome_category, amount=100)
        response = self.client.get(
            "{}?transaction_type={}".format(
                reverse("transaction-summary"), TransactionType.INCOME
            )
        )
        self.assertGreater(response.json()["total"], 0)

    def test_filter_time(self):
        """Mustn't summarize transactions that don't match the filter."""
        old_transactions_time = timezone.now() - timedelta(days=10)
        self.create_transactions_batch(
            50,
            category=self.income_category,
            amount=5,
            transaction_time=old_transactions_time,
        )
        response = self.client.get(
            "{}?transaction_time_after={}".format(
                reverse("transaction-summary"),
                quote((old_transactions_time + timedelta(seconds=1)).isoformat()),
            )
        )
        self.assertEqual(0, response.json()["total"])


class TransactionFilterTests(IncomeOutcomeCategoriesTestCase, BaseViewTestCase):
    def test_transaction_type_filter(self):
        """Response must contain only transactions of provided type."""
        self.create_transactions_batch(10, category=self.outcome_category)
        income_transactions = self.create_transactions_batch(
            5, category=self.income_category
        )
        self._test_list_count(
            "{}?category__transaction_type=IN".format(reverse("transaction-list")),
            len(income_transactions),
        )

    def test_other_account_category_filter(self):
        """Forbid displaying transactions that belong to another account."""
        other_account_category = self.create_category(account=AccountFactory())
        response = self.client.get(
            "{}?category={}".format(
                reverse("transaction-list"), other_account_category.id
            )
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            response.json()["category"],
            ["Select a valid choice. That choice is not one of the available choices."],
        )

    def test_category_filter(self):
        """Response must contain only transactions of provided category."""
        self.create_transactions_batch(5, category=self.create_category())
        selected_category = self.create_category()
        selected_category_transactions = self.create_transactions_batch(
            10, category=selected_category
        )
        self._test_list_count(
            "{}?category={}".format(reverse("transaction-list"), selected_category.id),
            len(selected_category_transactions),
        )
