from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from ..currency import CurrencyConverter
from ..currency_rates import BaseRates
from ...constants import CurrencyCode


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
            (Decimal("1"), Decimal("1"), Decimal("1"), CurrencyCode.BYN, CurrencyCode.EUR),
            (Decimal("25.5"), Decimal("0.233"), Decimal("5.94"), CurrencyCode.USD, CurrencyCode.EUR),
            (Decimal("124"), Decimal("0.00094"), Decimal("0.12"), CurrencyCode.RUB, CurrencyCode.BYN),
            (Decimal("1"), Decimal("0.0000001"), Decimal("0"), CurrencyCode.BYN, CurrencyCode.USD),
            (Decimal("0.03"), Decimal("70"), Decimal("2.1"), CurrencyCode.USD, CurrencyCode.RUB),
        ):
            with self.subTest(amount=amount, rate=rate, cur_from=cur_from, cur_to=cur_to):
                self.rates.get_rate.return_value = rate
                result = self.converter.convert(amount, cur_from, cur_to)
                self.assertEqual(result, expected_value)
