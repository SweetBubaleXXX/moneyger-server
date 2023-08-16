from django.urls import reverse
from rest_framework import status

from ...constants import TransactionType
from ..models import TransactionCategory
from .base import (
    BaseSummaryViewTestCase,
    BaseViewTestCase,
    IncomeOutcomeCategoriesTestCase,
    MockCurrencyConvertorMixin,
)
from .factories import AccountFactory


class TransactionCategoryViewTests(BaseViewTestCase):
    def test_list_categories_unauthorized(self):
        """Try to get categories list without providing authorization credentials."""
        self._test_get_unauthorized(reverse("transaction-category-list"))

    def test_no_categories(self):
        """Response must be empty if there are on categories."""
        self._test_list_count(reverse("transaction-category-list"), 0)

    def test_list_categories(self):
        """Response must contain correct amount of items."""
        self.create_categories_batch(10, account=AccountFactory())
        own_categories = self.create_categories_batch(5)
        self._test_list_count(reverse("transaction-category-list"), len(own_categories))

    def test_list_queries_number(self):
        """Correct number of queries must be performed."""
        self.create_categories_batch(5)
        self._test_get_queries_number(2, reverse("transaction-category-list"))

    def test_add_category_unauthorized(self):
        """Try to create category without providing authorization credentials."""
        self._test_post_unauthorized(
            reverse("transaction-category-list"),
            {
                "transaction_type": TransactionType.OUTCOME,
                "name": "Category",
            },
        )

    def test_add_category_required_fields(self):
        """
        Response an error when trying to create a category without necessary fields.
        """
        response = self.client.post(reverse("transaction-category-list"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("name", "transaction_type"):
            self.assertListEqual(response.json()[field], ["This field is required."])

    def test_add_category_blank_name(self):
        """Response an error when trying to create a category with blank name."""
        response = self.client.post(reverse("transaction-category-list"), {"name": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(response.json()["name"], ["This field may not be blank."])

    def test_add_category_null_parent(self):
        """Category must be created with parent_category set to null."""
        request_body = {
            "transaction_type": TransactionType.OUTCOME,
            "name": "Category",
        }
        response = self.client.post(reverse("transaction-category-list"), request_body)
        expected_response_subdict = request_body | {"parent_category": None}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertLessEqual(
            expected_response_subdict.items(),
            response.json().items(),
        )

    def test_add_category_ignore_parent(self):
        """Parent category id in request must be ignored when adding new."""
        request_body = {
            "parent_category": 12345,
            "transaction_type": TransactionType.OUTCOME,
            "name": "Category",
        }
        response = self.client.post(reverse("transaction-category-list"), request_body)
        self.assertEqual(response.json()["parent_category"], None)

    def test_add_category_queries_number(self):
        """Correct number of queries must be performed.

        One for adding new category, one for historical record.
        """
        self._test_post_queries_number(
            2,
            reverse("transaction-category-list"),
            data={
                "transaction_type": TransactionType.OUTCOME,
                "name": "Category",
            },
        )

    def test_category_not_found(self):
        """Response 404 if category doesn't exist."""
        response = self.client.get(
            reverse("transaction-category-detail", args=(12345,))
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_category_of_other_account(self):
        """Response 404 when trying to get category that belongs to another account."""
        other_account_category = self.create_category(account=AccountFactory())
        response = self.client.get(
            reverse("transaction-category-detail", args=(other_account_category.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_queries_number(self):
        """Correct number of queries must be performed."""
        category = self.create_category()
        self._test_get_queries_number(
            1,
            reverse("transaction-category-detail", args=(category.id,)),
            category_id=category.id,
        )

    def test_cannot_edit_transaction_type(self):
        """Forbid changing transaction type of existing category."""
        category = self.create_category(transaction_type=TransactionType.OUTCOME)
        response = self.client.patch(
            reverse("transaction-category-detail", args=(category.id,)),
            {"transaction_type": TransactionType.INCOME},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.json()["transaction_type"], TransactionType.INCOME)

    def test_updated_category(self):
        """Category must have provided fields changed."""
        category = self.create_category()
        request_body = {
            "name": "New name",
            "display_order": 10,
            "icon": "new_icon",
            "color": "#123456",
        }
        response = self.client.put(
            reverse("transaction-category-detail", args=(category.id,)), request_body
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(request_body.items(), response.json().items())

    def test_delete_category(self):
        """Category must be successfully deleted."""
        category = self.create_category()
        response = self.client.delete(
            reverse("transaction-category-detail", args=(category.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(TransactionCategory.DoesNotExist):
            TransactionCategory.objects.get(pk=category.id)

    def test_delete_category_with_subcategories(self):
        """All subcategories must be deleted too."""
        parent_category = self.create_category()
        subcategories = self.create_categories_batch(
            10, parent_category=parent_category
        )
        response = self.client.delete(
            reverse("transaction-category-detail", args=(parent_category.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        for category in subcategories:
            with self.assertRaises(TransactionCategory.DoesNotExist):
                TransactionCategory.objects.get(pk=category.id)


class TransactionCategorySummaryViewTests(
    MockCurrencyConvertorMixin, IncomeOutcomeCategoriesTestCase, BaseSummaryViewTestCase
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
            8,
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


class TransactionCategoryFilterTests(BaseViewTestCase):
    def test_categories_list_filter_not_subcategory(self):
        """Response list must contain only categories without parent category."""
        parent_categories = self.create_categories_batch(5)
        for category in parent_categories:
            self.create_categories_batch(3, parent_category=category)
        self._test_list_count(
            "{}?not_subcategory=True".format(reverse("transaction-category-list")),
            len(parent_categories),
        )

    def test_categories_display_order(self):
        """Categories with higher display order must be displayed first."""
        self.create_category()
        category = self.create_category(display_order=13)
        self.create_category()
        response = self.client.get(reverse("transaction-category-list"))
        first_category = response.json()["results"][0]
        self.assertEqual(first_category["id"], category.id)
