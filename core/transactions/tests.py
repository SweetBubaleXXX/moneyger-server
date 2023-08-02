from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..constants import TransactionType
from .factories import AccountFactory, TransactionCategoryFactory
from .models import TransactionCategory


class AuthorizedTestCase(TestCase):
    def setUp(self):
        self.account = AccountFactory()
        self.client = APIClient()
        self.client.force_login(self.account)


class TransactionCategoryViewTests(AuthorizedTestCase):
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
        categories = TransactionCategoryFactory.create_batch(
            5, account=self.account, parent_category=None
        )
        response = self.client.get(reverse("transaction-category-list"))
        response_list = response.json()
        self.assertIsInstance(response_list, list)
        self.assertEqual(len(response_list), len(categories))

    def test_category_not_found(self):
        """Response 404 if category doesn't exist."""
        response = self.client.post(reverse("transaction-category-list", args=(12345,)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_category_required_fields(self):
        """
        Response an error when trying to create a category without necessary fields.
        """
        response = self.client.post(reverse("transaction-category-list"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertListEqual(response.json()["name"], ["This field is required."])
        self.assertListEqual(
            response.json()["transaction_type"], ["This field is required."]
        )

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

    def test_cannot_edit_transaction_type(self):
        """Forbid changing transaction type of existing category."""
        category = TransactionCategoryFactory(
            account=self.account,
            parent_category=None,
            transaction_type=TransactionType.OUTCOME,
        )
        response = self.client.patch(
            reverse("transaction-category-detail", args=(category.id,)),
            {"transaction_type": TransactionType.INCOME},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.json()["transaction_type"], TransactionType.INCOME)

    def test_updated_category(self):
        """Category must have provided fields changed."""
        category = TransactionCategoryFactory(
            account=self.account,
            parent_category=None,
        )
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
        category = TransactionCategoryFactory(
            account=self.account,
            parent_category=None,
        )
        response = self.client.delete(
            reverse("transaction-category-detail", args=(category.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(TransactionCategory.DoesNotExist):
            TransactionCategory.objects.get(pk=category.id)

    def test_delete_category_with_subcategories(self):
        """All subcategories must be deleted too."""
        parent_category = TransactionCategoryFactory(
            account=self.account, parent_category=None
        )
        subcategories = TransactionCategoryFactory.create_batch(
            10, account=self.account, parent_category=parent_category
        )
        response = self.client.delete(
            reverse("transaction-category-detail", args=(parent_category.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        for category in subcategories:
            with self.assertRaises(TransactionCategory.DoesNotExist):
                TransactionCategory.objects.get(pk=category.id)


class TransactionCategoryFilterTests(AuthorizedTestCase):
    def test_categories_list_filter_not_subcategory(self):
        """Response list must contain only categories without parent category."""
        parent_categories = TransactionCategoryFactory.create_batch(
            5, account=self.account, parent_category=None
        )
        for category in parent_categories:
            TransactionCategoryFactory.create_batch(
                3, account=self.account, parent_category=category
            )
        response = self.client.get(
            "%s?not_subcategory=True" % reverse("transaction-category-list")
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), len(parent_categories))


class TransactionSubcategoryViewTests(AuthorizedTestCase):
    def test_no_subcategories(self):
        """Response must be an empty list if there are on subcategories."""
        parent_category = TransactionCategoryFactory(
            account=self.account, parent_category=None
        )
        response = self.client.get(
            reverse("transaction-category-subcategories", args=(parent_category.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json(), [])

    def test_list_subcategories_of_other_account(self):
        """Response 404 when trying to get subcategories of other account."""
        other_account_category = TransactionCategoryFactory(
            account=AccountFactory(),
            parent_category=None,
        )
        response = self.client.get(
            reverse(
                "transaction-category-subcategories", args=(other_account_category.id,)
            )
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subcategories_list_amount(self):
        """Response list must contain correct amount of items."""
        parent_category = TransactionCategoryFactory(
            account=self.account, parent_category=None
        )
        categories = TransactionCategoryFactory.create_batch(
            10, account=self.account, parent_category=parent_category
        )
        response = self.client.get(
            reverse("transaction-category-subcategories", args=(parent_category.id,))
        )
        response_list = response.json()
        self.assertIsInstance(response_list, list)
        self.assertEqual(len(response_list), len(categories))

    def test_add_subcategory_to_other_account(self):
        """Response 404 when trying to add subcategory to other account."""
        other_account_category = TransactionCategoryFactory(
            account=AccountFactory(),
            parent_category=None,
        )
        response = self.client.post(
            reverse(
                "transaction-category-subcategories", args=(other_account_category.id,)
            ),
            {"name": "Subcategory"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_subcategory_nonexistent_parent(self):
        """Response 404 if trying to add subcategory to category that doesn't exist"""
        response = self.client.post(
            reverse("transaction-category-subcategories", args=(12345,))
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_subcategory(self):
        """Subcategory must be created and have the same transaction_type."""
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
