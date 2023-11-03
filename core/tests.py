from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase

from moneymanager import services_container

from .services.currency import CurrencyConverter


class CacheClearMixin(TestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(cache.clear)


class MockCurrencyConvertorMixin(TestCase):
    CONVERSION_RATE = Decimal(2)

    def setUp(self):
        super().setUp()
        self.converter_mock = MagicMock(CurrencyConverter)
        self.converter_mock.convert.side_effect = (
            lambda amount, *_: amount * self.CONVERSION_RATE
        )
        services_container.override(CurrencyConverter, self.converter_mock)

    def tearDown(self):
        super().tearDown()
        services_container.reset_override()


class StopPatchersMixin(TestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(patch.stopall)
