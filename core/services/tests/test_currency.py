from decimal import Decimal
from unittest.mock import MagicMock

from django.test import TestCase
from iso4217 import Currency

from ...constants import CurrencyCode
from ..currency import CurrencyConverter
from ..rates_providers import BaseRates


def test_currency_metadata():
    """No exception must be raised when getting currency info."""
    for currency in CurrencyCode:
        Currency(currency)


class CurrencyConverterTestCase(TestCase):
    def setUp(self):
        self.rates = MagicMock(BaseRates)
        self.rates.get_rate.return_value = Decimal(1)
        self.converter = CurrencyConverter(self.rates)

    def test_rates_mock(self):
        """get_rate mock must be called with appropriate args."""
        self.converter.convert(Decimal(10), CurrencyCode.RUB, CurrencyCode.EUR)
        self.rates.get_rate.assert_called_once_with(CurrencyCode.RUB, CurrencyCode.EUR)

    def test_convert(self):
        """Must return correct result."""
        for amount, rate, expected_value, cur_from, cur_to in (
            ("1", "1", "1", CurrencyCode.BYN, CurrencyCode.EUR),
            ("25.5", "0.233", "5.94", CurrencyCode.USD, CurrencyCode.EUR),
            ("124", "0.00094", "0.12", CurrencyCode.RUB, CurrencyCode.BYN),
            ("1", "0.0000001", "0", CurrencyCode.BYN, CurrencyCode.USD),
            ("0.03", "70", "2.1", CurrencyCode.USD, CurrencyCode.RUB),
        ):
            with self.subTest(
                amount=amount, rate=rate, cur_from=cur_from, cur_to=cur_to
            ):
                self.rates.get_rate.return_value = Decimal(rate)
                result = self.converter.convert(Decimal(amount), cur_from, cur_to)
                self.assertEqual(result, Decimal(expected_value))
