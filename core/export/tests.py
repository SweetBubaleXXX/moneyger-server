from django.urls import reverse
from rest_framework import status

from ..constants import CurrencyCode, TransactionType
from ..transactions.tests.base import BaseViewTestCase
from ..transactions.tests.factories import AccountFactory


class ExportCsvViewTests(BaseViewTestCase):
    def test_unauthorized(self):
        """Try to get data without providing authorization credentials."""
        self._test_get_unauthorized(reverse("export-csv"))

    def test_no_transactions(self):
        """Test export when there are no transactions."""

        self._test_header(self._get_csv_response())

    def test_export(self):
        """Test export transactions."""
        category = self.create_category(
            name="Expenses category", transaction_type=TransactionType.OUTCOME
        )
        transactions = self.create_transactions_batch(
            10, category=category, currency=CurrencyCode.USD
        )
        response_iterator = self._iter_csv_response()
        self._test_header(next(response_iterator))
        rows = list(response_iterator)
        self.assertEqual(len(rows), len(transactions))
        for row in rows:
            self.assertRegex(
                row, r"^Expenses category,OUT,USD,[0-9]+(\.[0-9]+)?,.*\r\n$"
            )

    def test_view_data_of_other_account(self):
        """Transactions that belong to another account mustn't be present."""
        self.create_transactions_batch(5, account=AccountFactory())
        own_transactions = self.create_transactions_batch(10)
        response = list(self._iter_csv_response())
        self.assertEqual(len(response), len(own_transactions) + 1)

    def test_queries_number(self):
        """Correct number of queries must be performed."""
        self.create_transactions_batch(20)
        with self.assertNumQueries(2):
            self._get_csv_response()

    def _test_header(self, header):
        self.assertEqual(
            header,
            "category,transaction_type,currency,amount,transaction_time,comment\r\n",
        )

    def _get_csv_response(self):
        return "".join(self._iter_csv_response())

    def _iter_csv_response(self):
        response = self.client.get(reverse("export-csv"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers["Content-Type"], "text/csv")
        for line in response.streaming_content:
            yield line.decode()


class ExportJsonViewTests(BaseViewTestCase):
    def test_unauthorized(self):
        """Try to get data without providing authorization credentials."""
        self._test_get_unauthorized(reverse("export-json"))

    def test_view_data_of_other_account(self):
        """Categories that belong to another account mustn't be present."""
        self.create_categories_batch(10, account=AccountFactory())
        response = self.client.get(reverse("export-json"))
        self.assertListEqual(response.json(), [])

    def test_no_categories(self):
        """Must return empty list if there are no categories."""
        response = self.client.get(reverse("export-json"))
        self.assertListEqual(response.json(), [])

    def test_nested_categories(self):
        """All subcategories and transactions must be present."""
        categories = self.create_categories_batch(5)
        for category in categories:
            for subcategory in self.create_categories_batch(
                3, parent_category=category
            ):
                self.create_transactions_batch(10, category=subcategory)
        response = self.client.get(reverse("export-json")).json()
        self.assertEqual(len(response), len(categories))
        for category in response:
            self.assertEqual(len(category["subcategories"]), 3)
            self.assertListEqual(category["transactions"], [])
            for subcategory in category["subcategories"]:
                self.assertEqual(len(subcategory["transactions"]), 10)

    def test_queries_number(self):
        """Correct number of queries must be performed."""
        for category in self.create_categories_batch(5):
            self.create_categories_batch(3, parent_category=category)
        self._test_get_queries_number(33, reverse("export-json"))
