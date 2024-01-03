from copy import deepcopy

from django.urls import reverse
from rest_framework import status

from core.transactions.models import Transaction, TransactionCategory
from core.transactions.tests.base import BaseViewTestCase

from .constants import EXPORTED_CATEGORIES


class ImportJsonViewTests(BaseViewTestCase):
    def test_unauthorized(self):
        """Try to send data without providing authorization credentials."""
        self.client.logout()
        self._test_post_unauthorized(reverse("import-json"), {})

    def test_invalid_format(self):
        """Must response an error if data is not in appropriate format."""
        response = self.client.post(reverse("import-json"), "text")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_data(self):
        """Must response an error if data is invalid."""
        response = self.client.post(
            reverse("import-json"),
            {
                "a": [1, 2, 3],
                "b": {
                    "c": 1,
                    "d": 2,
                },
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_atomic(self):
        """Must rollback if an error occured during import."""
        broken_data = deepcopy(EXPORTED_CATEGORIES)
        first_category = broken_data[0]
        first_subcategory = first_category["subcategories"][0]
        first_subcategory["transaction_type"] = "invalid value"
        response = self.client.post(reverse("import-json"), broken_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        categories_count = self.account.transactioncategory_set.count()
        self.assertEqual(categories_count, 0)

    def test_import(self):
        """All categories and transactions must be imported."""
        response = self.client.post(reverse("import-json"), EXPORTED_CATEGORIES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transaction.objects.count(), 4)
        self.assertEqual(TransactionCategory.objects.count(), 8)
        subcategories_count = TransactionCategory.objects.filter(
            parent_category__isnull=False
        ).count()
        self.assertEqual(subcategories_count, 6)

    def test_transactions_added_notification(self):
        """Imported transactions must be sent to notifications service."""
        response = self.client.post(reverse("import-json"), EXPORTED_CATEGORIES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.publisher_mock.add_message.assert_called_once()
        self.publisher_mock.publish.assert_called_once()

    def test_queries_number(self):
        """Correct number of queries must be performed."""
        self._test_post_queries_number(5, reverse("import-json"), EXPORTED_CATEGORIES)
