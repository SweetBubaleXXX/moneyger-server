from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..constants import TransactionType
from .factories import (
    DEFAULT_ACCOUNT_PASSWORD,
    AccountFactory,
    TransactionCategoryFactory,
)


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
        """Response must be an empty list if there are on categories."""
        response = self.client.get(reverse("transaction-category-list"))
        self.assertListEqual(response.json(), [])

    def test_categories_list_amount(self):
        """Response list must contain correct amount of items."""
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

    def test_add_category_required_fields(self):
        """
        Response an error when trying to create a category without necessary fields.
        """
        response = self.client.post(reverse("transaction-category-list"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(response.json().get("name"), ["This field is required."])
        self.assertListEqual(
            response.json().get("transaction_type"), ["This field is required."]
        )

    def test_add_category_blank_name(self):
        """Response an error when trying to create a category with blank name."""
        response = self.client.post(reverse("transaction-category-list"), {"name": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(
            response.json().get("name"), ["This field may not be blank."]
        )

    def test_add_category_null_parent(self):
        """Category must be created with parent_category set to null."""
        request_body = {
            "transaction_type": TransactionType.OUTCOME,
            "name": "Category",
        }
        response = self.client.post(reverse("transaction-category-list"), request_body)
        expected_response_subdict = request_body | {"parent_category": None}
        self.assertLessEqual(
            expected_response_subdict.items(),
            response.json().items(),
        )

    def test_add_subcategory(self):
        """Subcategory should be created and have the same transaction_type."""
        parent_category = TransactionCategoryFactory(
            account=self.account,
            parent_category=None,
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
