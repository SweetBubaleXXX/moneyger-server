from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from rest_framework import status

from core.tests import CacheClearMixin

from ...constants import CurrencyCode
from ..rates_providers import AlfaBankNationalRates, FetchRatesException
from . import rates_responses


class AlfaBankNationalRatesTestCase(CacheClearMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.rates = AlfaBankNationalRates()
        self.patcher = patch("requests.get")
        self.RequestMock = self.patcher.start()
        self._set_response_status_code(status.HTTP_200_OK)
        self._set_response_json_body(rates_responses.ALFA_BANK_NATIONAL_RATES_RESPONSE)

    def _set_response_status_code(self, code):
        self.RequestMock.return_value.status_code = code

    def _set_response_json_body(self, body):
        self.RequestMock.return_value.json.return_value = body

    def test_request_mock(self):
        """RequestMock must be called with appropriate args."""
        self.rates.fetch_data()
        self.RequestMock.assert_called_once_with(settings.ALFA_BANK_NATIONAL_RATES_URL)

    def test_fetch_data_response_error_code(self):
        """
        FetchRatesException must be raised if API response has non 200 status code.
        """
        self._set_response_status_code(status.HTTP_400_BAD_REQUEST)
        with self.assertRaises(FetchRatesException):
            self.rates.fetch_data()

    def test_fetch_data_empty_rates(self):
        """FetchRatesException must be raised if API response has empty rates list."""
        self._set_response_json_body({"rates": []})
        with self.assertRaises(FetchRatesException):
            self.rates.fetch_data()

    def test_fetch_data_return_value(self):
        """Fetched data must contain rates only for currencies from CurrencyCode."""
        fetched_data = self.rates.fetch_data()
        for currency in fetched_data.keys():
            self.assertIn(currency, CurrencyCode)

    def test_unsupported_currencies(self):
        """
        ValueError with correct message must be raised if currency isn't supported.
        """
        unsupported_currency = "ABC"
        self.assertNotIn(unsupported_currency, self.rates.supported_currencies)
        with self.assertRaisesMessage(
            ValueError, f"No rates for {unsupported_currency}"
        ):
            self.rates.get_rate(CurrencyCode.EUR, unsupported_currency)

    def test_get_data_empty_cache(self):
        """fetch_data method must be called when no data in cache."""
        self.rates.get_data()
        self.RequestMock.assert_called_once()

    def test_get_data_cache(self):
        """fetch_data method mustn't be called when data in cache."""
        self.rates.get_data()
        self.rates.get_data()
        self.RequestMock.assert_called_once()

    def test_get_data_types(self):
        """get_data method response must have correct type."""
        rates = self.rates.get_data()
        self.assertIsInstance(rates, dict)
        for key in rates.keys():
            self.assertIsInstance(key, str)
        for value in rates.values():
            self.assertIsInstance(value, Decimal)

    def test_get_rate_same_currency(self):
        """Must return 1 when cur_from and cur_to are the same."""
        rate = self.rates.get_rate(CurrencyCode.USD, CurrencyCode.USD)
        self.assertIsInstance(rate, Decimal)
        self.assertEqual(rate, Decimal(1))

    def test_get_rate_to_byn(self):
        """Must return correct rate."""
        rate = self.rates.get_rate(CurrencyCode.USD, CurrencyCode.BYN)
        self.assertEqual(rate, Decimal("3.1543"))

    def test_get_rate_from_byn(self):
        """Must return correct rate."""
        rate = self.rates.get_rate(CurrencyCode.BYN, CurrencyCode.RUB)
        self.assertEqual(
            round(rate, 6),
            round(Decimal("30.5586114167"), 6),
        )

    def test_get_rate_arbitrary(self):
        rate = self.rates.get_rate(CurrencyCode.EUR, CurrencyCode.USD)
        self.assertEqual(
            round(rate, 6),
            round(Decimal("1.0967568082"), 6),
        )
