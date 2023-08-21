import re

from ..constants import CurrencyCode
from ..transactions.tests.base import BaseTestCase
from .services import csv_generator


class ExportCsvTestCase(BaseTestCase):
    def test_no_transactions(self):
        """Test export when there are no transactions."""
        csv_output = self._get_csv_output([])
        self._test_header(csv_output)

    def test_export(self):
        """Test export transactions."""
        category = self.create_category()
        transactions = self.create_transactions_batch(
            10, category=category, amount=1234, currency=CurrencyCode.USD
        )
        csv_output = csv_generator(transactions)
        self._test_header(next(csv_output))
        rows = list(csv_output)
        self.assertEqual(len(rows), len(transactions))
        pattern = re.compile(
            rf"^{category.name},{category.transaction_type},{CurrencyCode.USD},12.34,.*\r\n$"
        )
        for row in rows:
            self.assertRegex(row, pattern)

    def _test_header(self, header):
        self.assertEqual(
            header,
            "category,transaction_type,currency,amount,transaction_time,comment\r\n",
        )

    def _get_csv_output(self, transactions):
        return "".join(csv_generator(transactions))
