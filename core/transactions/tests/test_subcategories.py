from django.urls import reverse
from rest_framework import status

from .base import BaseViewTestCase
from .factories import AccountFactory


class TransactionSubcategoryViewTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.parent_category = self.create_category()

    def test_no_subcategories(self):
        """Response must be empty if there are on subcategories."""
        self._test_list_count(
            reverse(
                "transaction-category-subcategories", args=(self.parent_category.id,)
            ),
            0,
        )

    def test_list_subcategories_of_other_account(self):
        """Response 404 when trying to get subcategories of other account."""
        other_account_category = self.create_category(account=AccountFactory())
        response = self.client.get(
            reverse(
                "transaction-category-subcategories", args=(other_account_category.id,)
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_subcategories(self):
        """Response must contain correct amount of items."""
        categories = self.create_categories_batch(
            10, parent_category=self.parent_category
        )
        self._test_list_count(
            reverse(
                "transaction-category-subcategories", args=(self.parent_category.id,)
            ),
            len(categories),
        )

    def test_list_queries_number(self):
        """Exactly 3 queries must be performed."""
        self._test_get_queries_number(
            3,
            reverse(
                "transaction-category-subcategories", args=(self.parent_category.id,)
            ),
            category_id=self.parent_category.id,
        )

    def test_list_subcategories_recursive(self):
        """Response must contain subcategories of subcategories."""
        parent_category = self.create_category()
        categories = self.create_categories_batch(10, parent_category=parent_category)
        for subcategory in categories:
            self.create_categories_batch(5, parent_category=subcategory)
        response = self.client.get(
            reverse("transaction-category-subcategories", args=(parent_category.id,))
        )
        self.assertEqual(response.json()["count"], 60)

    def test_add_subcategory_to_other_account(self):
        """Response 404 when trying to add subcategory to other account."""
        other_account_category = self.create_category(
            account=AccountFactory(),
        )
        response = self.client.post(
            reverse(
                "transaction-category-subcategories", args=(other_account_category.id,)
            ),
            {"name": "Subcategory"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_subcategory_nonexistent_parent(self):
        """Response 404 if trying to add subcategory to category that doesn't exist."""
        response = self.client.post(
            reverse("transaction-category-subcategories", args=(12345,))
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_subcategory(self):
        """Subcategory must be created and have the same transaction_type."""
        request_body = {"name": "Subcategory"}
        response = self.client.post(
            reverse(
                "transaction-category-subcategories", args=(self.parent_category.id,)
            ),
            request_body,
        )
        expected_response_subdict = request_body | {
            "parent_category": self.parent_category.id,
            "transaction_type": self.parent_category.transaction_type,
        }
        self.assertLessEqual(
            expected_response_subdict.items(),
            response.json().items(),
        )

    def test_add_subcategory_queries_number(self):
        """Exactly 3 queries must be performed."""
        self._test_post_queries_number(
            3,
            reverse(
                "transaction-category-subcategories",
                args=(self.parent_category.id,),
            ),
            data={"name": "Subcategory"},
            category_id=self.parent_category.id,
        )
