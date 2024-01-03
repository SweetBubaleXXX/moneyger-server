from decimal import Decimal

from core.constants import CurrencyCode
from core.tests import MockCurrencyConvertorMixin

from ..services import compute_total
from ..utils import get_all_subcategories, get_all_transactions
from .base import BaseTestCase, IncomeOutcomeCategoriesMixin


class ComputeTotalTestCase(MockCurrencyConvertorMixin, IncomeOutcomeCategoriesMixin):
    def test_no_transactions(self):
        """Must return 0 if there are no transactions."""
        total = compute_total([], CurrencyCode.RUB)
        self.assertEqual(total, Decimal(0))

    def test_income_no_conversion(self):
        """Must return correct positive value."""
        transactions = self.create_transactions_batch(
            30, category=self.income_category, amount=200, currency=CurrencyCode.USD
        )
        total = compute_total(transactions, CurrencyCode.USD)
        self.assertEqual(total, Decimal(60))

    def test_outcome_no_conversion(self):
        """Must return correct negative value."""
        transactions = self.create_transactions_batch(
            50, category=self.outcome_category, amount=300, currency=CurrencyCode.EUR
        )
        total = compute_total(transactions, CurrencyCode.EUR)
        self.assertEqual(total, Decimal(-150))

    def test_income_and_outcome_no_conversion(self):
        """Must treat income as positive value and outcome as negative."""
        income_transactions = self.create_transactions_batch(
            30, category=self.income_category, amount=200, currency=CurrencyCode.BYN
        )
        outcome_transactions = self.create_transactions_batch(
            50, category=self.outcome_category, amount=300, currency=CurrencyCode.BYN
        )
        total = compute_total(
            income_transactions + outcome_transactions, CurrencyCode.BYN
        )
        self.assertEqual(total, Decimal(-90))

    def test_conversion_called(self):
        """Must convert currencies if output currency is different."""
        transactions = self.create_transactions_batch(
            10, category=self.income_category, amount=10, currency=CurrencyCode.USD
        )
        compute_total(transactions, CurrencyCode.BYN)
        self.converter_mock.convert.assert_called_with(
            Decimal("0.1"), CurrencyCode.USD, CurrencyCode.BYN
        )

    def test_conversion_multiple_currencies(self):
        """Must return correct total of transactions with different currencies."""
        usd_transactions = self.create_transactions_batch(
            10, category=self.income_category, amount=500, currency=CurrencyCode.USD
        )
        byn_transactions = self.create_transactions_batch(
            5, category=self.income_category, amount=2000, currency=CurrencyCode.BYN
        )
        total = compute_total(usd_transactions + byn_transactions, CurrencyCode.BYN)
        self.assertEqual(total, Decimal("50") * self.CONVERSION_RATE + Decimal("100"))


class GetAllSubcategoriesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category = self.create_category()

    def test_no_subcategories(self):
        """Must return empty QuerySet."""
        subcategories = get_all_subcategories(self.category)
        self.assertFalse(subcategories)

    def test_depth_1(self):
        """Test subcategory tree of depth 1."""
        self.create_categories_batch(10, parent_category=self.category)
        subcategories = get_all_subcategories(self.category)
        self.assertEqual(subcategories.count(), 10)

    def test_depth_2(self):
        """Test subcategory tree of depth 2."""
        child_categories = self.create_categories_batch(
            10, parent_category=self.category
        )
        for category in child_categories:
            self.create_categories_batch(20, parent_category=category)
        subcategories = get_all_subcategories(self.category)
        self.assertEqual(subcategories.count(), 210)

    def test_depth_3(self):
        """Test subcategory tree of depth 3."""
        child_categories = self.create_categories_batch(
            5, parent_category=self.category
        )
        for category in child_categories:
            for subcategory in self.create_categories_batch(
                10, parent_category=category
            ):
                self.create_categories_batch(5, parent_category=subcategory)
        subcategories = get_all_subcategories(self.category)
        self.assertEqual(subcategories.count(), 305)


class GetAllTransactionsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category = self.create_category()

    def test_depth_1(self):
        """Must return all transactions of subcategory tree with depth 1."""
        self.create_transactions_batch(3, category=self.category)
        for category in self.create_categories_batch(10, parent_category=self.category):
            self.create_transactions_batch(5, category=category)
        transactions = get_all_transactions(self.category)
        self.assertEqual(transactions.count(), 53)

    def test_depth_2(self):
        """Must return all transactions of subcategory tree with depth 2."""
        child_categories = self.create_categories_batch(
            10, parent_category=self.category
        )
        for category in child_categories:
            self.create_transactions_batch(4, category=category)
            for subcategory in self.create_categories_batch(
                3, parent_category=category
            ):
                self.create_transactions_batch(5, category=subcategory)
        transactions = get_all_transactions(self.category)
        self.assertEqual(transactions.count(), 190)
