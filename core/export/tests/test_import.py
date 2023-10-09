from django.urls import reverse
from rest_framework import status

from ...transactions.tests.base import BaseViewTestCase
from .contants import EXPORTED_CATEGORIES


class ImportJsonViewTests(BaseViewTestCase):
    def test_unauthorized(self):
        """Try to send data without providing authorization credentials."""
        self.client.logout()
        self._test_post_unauthorized(reverse("import-json"), {})

    def test_empty_body(self):
        """Must response an error if request has no data."""
        response = self.client.post(reverse("import-json"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_format(self):
        """Must response an error if data is not in appropriate format."""
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
        broken_data = EXPORTED_CATEGORIES.copy()
        broken_data[1]["transaction_type"] = "invalid value"
        response = self.client.post(reverse("import-json"), broken_data)
        self.assertEqual(response.status_code)
        transactions_count = self.account.transaction_set.count()
        self.assertEqual(transactions_count, 0)

    def test_import(self):
        """All categories and transactions must be imported."""
        response = self.client.post(reverse("import-json"), EXPORTED_CATEGORIES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
