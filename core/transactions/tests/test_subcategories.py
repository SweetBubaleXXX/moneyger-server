from django.urls import reverse
from rest_framework import status

from ...constants import TransactionType
from .base import BaseTestCase
from .factories import AccountFactory


class TransactionSubcategoryViewTests(BaseTestCase):
    def test_no_subcategories(self):
        """Response must be empty if there are on subcategories."""
        parent_category = self.create_category()
        response = self.client.get(
            reverse("transaction-category-subcategories", args=(parent_category.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

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
        parent_category = self.create_category()
        categories = self.create_categories_batch(10, parent_category=parent_category)
        response = self.client.get(
            reverse("transaction-category-subcategories", args=(parent_category.id,))
        )
        self.assertEqual(response.json()["count"], len(categories))

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
        parent_category = self.create_category(
            transaction_type=TransactionType.INCOME,
        )
        request_body = {"name": "Subcategory"}
        response = self.client.post(
            reverse("transaction-category-subcategories", args=(parent_category.id,)),
            request_body,
        )
        expected_response_subdict = request_body | {
            "parent_category": parent_category.id,
            "transaction_type": parent_category.transaction_type,
        }
        self.assertLessEqual(
            expected_response_subdict.items(),
            response.json().items(),
        )
