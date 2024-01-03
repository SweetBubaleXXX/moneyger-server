from datetime import timedelta
from unittest.mock import patch
from urllib.parse import quote

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from core.constants import CurrencyCode, TransactionType
from core.tests import StopPatchersMixin
from core.transactions.tests.base import BaseTestCase, BaseViewTestCase
from core.transactions.tests.factories import AccountFactory

from ..tasks import generate_json


class GenerateJsonTestCase(BaseTestCase):
    def test_no_categories(self):
        """Must return empty list if there are no categories."""
        result = generate_json(self.account.id)
        self.assertListEqual(result, [])

    def test_nested_categories(self):
        """All subcategories and transactions must be present."""
        categories = self.create_categories_batch(5)
        for category in categories:
            for subcategory in self.create_categories_batch(
                3, parent_category=category
            ):
                self.create_transactions_batch(10, category=subcategory)
        result = generate_json(self.account.id)
        self.assertEqual(len(result), len(categories))
        for category in result:
            self.assertEqual(len(category["subcategories"]), 3)
            self.assertListEqual(category["transactions"], [])
            for subcategory in category["subcategories"]:
                self.assertEqual(len(subcategory["transactions"]), 10)

    def test_queries_number(self):
        """Correct number of queries must be performed."""
        for category in self.create_categories_batch(4):
            self.create_categories_batch(3, parent_category=category)
        with self.assertNumQueries(5):
            generate_json(self.account.id)


class ExportJsonViewTests(StopPatchersMixin, BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.generate_json_mock = patch(
            "core.export.views.generate_json",
        ).start()
        self.generate_json_mock.delay.return_value.id = "id"
        self.result_mock = patch("core.export.views.AsyncResult").start()
        self.task_result_mock = self.result_mock.return_value
        self.task_result_mock.result = []
        self.task_result_mock.ready.return_value = False
        self.task_result_mock.failed.return_value = False

    def test_unauthorized(self):
        """Try to get data without providing authorization credentials."""
        self._test_get_unauthorized(reverse("export-json"))

    def test_task_called(self):
        """Task for generating json must be called with correct account id."""
        self.client.get(reverse("export-json"))
        self.generate_json_mock.delay.assert_called_once_with(self.account.id)

    def test_accepted(self):
        """Must response 202 status for the first call."""
        response = self.client.get(reverse("export-json"))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_task_pending(self):
        """Must response 202 unless task is ready."""
        for _ in range(4):
            response = self.client.get(reverse("export-json"))
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.generate_json_mock.delay.assert_called_once()
        self.result_mock.assert_called_with("id")

    def test_task_result(self):
        """Must response result when task is ready."""
        response = self.client.get(reverse("export-json"))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.task_result_mock.ready.return_value = True
        response = self.client.get(reverse("export-json"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)


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
        with self.assertNumQueries(4):
            self._get_csv_response()

    def test_filter(self):
        """Mustn't export transactions that don't match the filter."""
        transaction_time = timezone.now() - timedelta(days=10)
        boundary_time = transaction_time + timedelta(seconds=1)
        self.create_transactions_batch(20, transaction_time=transaction_time)
        response = self.client.get(
            "{}?transaction_time_after={}".format(
                reverse("export-csv"),
                quote(boundary_time.isoformat()),
            )
        )
        self.assertEqual(len(list(response.streaming_content)), 1)

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
