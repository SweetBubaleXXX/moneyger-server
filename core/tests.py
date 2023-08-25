from decimal import Decimal
from unittest.mock import MagicMock

from django.core.cache import cache
from django.test import TestCase

from moneymanager import services_container

from .services.currency import CurrencyConverter


class CacheClearMixin(TestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(cache.clear)


class MockCurrencyConvertorMixin(TestCase):
    CONVERTION_RATE = Decimal(2)

    def setUp(self):
        super().setUp()
        self.converter_mock = MagicMock(CurrencyConverter)
        self.converter_mock.convert.side_effect = (
            lambda amount, *_: amount * self.CONVERTION_RATE
        )
        services_container.override(CurrencyConverter, self.converter_mock)

    def tearDown(self):
        super().tearDown()
        services_container.reset_override()
