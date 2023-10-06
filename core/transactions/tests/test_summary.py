from django.urls import reverse
from rest_framework import status

from core.tests import MockCurrencyConvertorMixin
from core.transactions.tests.base import (
    BaseSummaryViewTestCase,
    IncomeOutcomeCategoriesMixin,
)

from ...constants import TransactionType


class TransactionCategorySummaryViewTests(
    MockCurrencyConvertorMixin, IncomeOutcomeCategoriesMixin, BaseSummaryViewTestCase
):
    def test_unauthorized(self):
        """Try to get summary without providing authorization credentials."""
        self._test_get_unauthorized(
            reverse("transaction-category-summary", args=(self.income_category.id,))
        )

    def test_no_transactions(self):
        """Total value in response must be 0 if there are no transactions."""
        self._test_total_value(
            reverse("transaction-category-summary", args=(self.income_category.id,)), 0
        )

    def test_income_total_value(self):
        """Total value must be positive."""
        self.create_transactions_batch(10, category=self.income_category)
        self._test_positive_total(
            reverse("transaction-category-summary", args=(self.income_category.id,))
        )

    def test_outcome_total_value(self):
        """Total value must be negative."""
        self.create_transactions_batch(10, category=self.outcome_category)
        self._test_negative_total(
            reverse("transaction-category-summary", args=(self.outcome_category.id,))
        )

    def test_include_subcategories(self):
        """Transactions of subcategories must be computed too."""
        subcategories = self.create_categories_batch(
            5, parent_category=self.outcome_category
        )
        for category in subcategories:
            self.create_transactions_batch(
                15, category=category, amount=1, currency=self.account.default_currency
            )
        self._test_total_value(
            reverse("transaction-category-summary", args=(self.outcome_category.id,)),
            -0.75,
        )

    def test_queries_number(self):
        """Correct number of queries must be performed."""
        subcategories = self.create_categories_batch(
            5, parent_category=self.outcome_category
        )
        for category in subcategories:
            self.create_transactions_batch(15, category=category)
        self._test_get_queries_number(
            4,
            reverse("transaction-category-summary", args=(self.outcome_category.id,)),
            category_id=self.outcome_category.id,
        )

    def test_filter_time(self):
        """Mustn't summarize transactions that don't match the filter."""
        with self._test_filter_time(
            reverse("transaction-category-summary", args=(self.income_category.id,))
        ) as transaction_time:
            self.create_transactions_batch(
                20,
                category=self.income_category,
                transaction_time=transaction_time,
            )


class TransactionCategoryStatsViewTest(
    MockCurrencyConvertorMixin, BaseSummaryViewTestCase
):
    def test_unauthorized(self):
        """Try to get stats without providing authorization credentials."""
        self._test_get_unauthorized(reverse("transaction-category-stats"))

    def test_no_transactions(self):
        """Total value in response must be 0 if there are no transactions."""
        self._test_total_value(reverse("transaction-category-stats"), 0)

    def test_no_categories(self):
        """Categories list must be empty if there are none."""
        response = self.client.get(reverse("transaction-category-stats"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json()["categories"], [])

    def test_only_primary_categories(self):
        """Must summarize only primary categories by default."""
        primary_categories = self.create_categories_batch(10)
        for category in primary_categories:
            self.create_categories_batch(3, parent_category=category)
        response = self.client.get(reverse("transaction-category-stats"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["categories"]), len(primary_categories))

    def test_filter_parent_category(self):
        """Must display stats for subcategories of provided category."""
        parent_category = self.create_category()
        subcategories = self.create_categories_batch(
            15, parent_category=parent_category
        )
        response = self.client.get(reverse("transaction-category-stats"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["categories"]), len(subcategories))

    def test_filter_transaction_type(self):
        """Must include only categories of provided type."""
        self.create_categories_batch(7, transaction_type=TransactionType.INCOME)
        outcome_categories = self.create_categories_batch(
            9, transaction_type=TransactionType.OUTCOME
        )
        response = self.client.get(
            "{}?transaction_type=OUT".format(reverse("transaction-category-stats"))
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["categories"]), len(outcome_categories))

    def test_filter_time(self):
        """Mustn't summarize transactions that don't match the filter."""
        with self._test_filter_time(
            reverse("transaction-category-stats")
        ) as transaction_time:
            self.create_transactions_batch(
                15,
                category=self.create_category(),
                transaction_time=transaction_time,
            )


class TransactionSummaryViewTests(
    MockCurrencyConvertorMixin, IncomeOutcomeCategoriesMixin, BaseSummaryViewTestCase
):
    def test_unauthorized(self):
        """Try to get summary without providing authorization credentials."""
        self._test_get_unauthorized(reverse("transaction-summary"))

    def test_no_transactions(self):
        """Total value in response must be 0 if there are no transactions."""
        self._test_total_value(reverse("transaction-summary"), 0)

    def test_queries_number(self):
        """Correct number of queries must be performed."""
        self.create_transactions_batch(5)
        self._test_get_queries_number(1, reverse("transaction-summary"))

    def test_currency(self):
        """Must use account's default currency."""
        self._test_currency(reverse("transaction-summary"))

    def test_filter_outcome(self):
        """Total value must be negative."""
        self.create_transactions_batch(10, category=self.income_category, amount=100)
        self.create_transactions_batch(5, category=self.outcome_category, amount=100)
        self._test_negative_total(
            "{}?transaction_type={}".format(
                reverse("transaction-summary"), TransactionType.OUTCOME
            )
        )

    def test_filter_income(self):
        """Total value must be positive."""
        self.create_transactions_batch(5, category=self.income_category, amount=100)
        self.create_transactions_batch(10, category=self.outcome_category, amount=100)
        self._test_positive_total(
            "{}?transaction_type={}".format(
                reverse("transaction-summary"), TransactionType.INCOME
            )
        )

    def test_filter_time(self):
        """Mustn't summarize transactions that don't match the filter."""
        with self._test_filter_time(reverse("transaction-summary")) as transaction_time:
            self.create_transactions_batch(
                50,
                category=self.income_category,
                transaction_time=transaction_time,
            )
