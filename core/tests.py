from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import TestCase

from moneymanager import services_container

from .services.currency import CurrencyConverter
from .services.notifications.publishers import Publisher
from .services.notifications.transactions import TransactionsProducer
from .services.notifications.users import UsersProducer


class CacheClearMixin(TestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(cache.clear)


class ContainerResetOverrideMixin(TestCase):
    def tearDown(self):
        super().tearDown()
        services_container.reset_override()


class MockCurrencyConvertorMixin(ContainerResetOverrideMixin):
    CONVERSION_RATE = Decimal(2)

    def setUp(self):
        super().setUp()
        self.converter_mock = MagicMock(CurrencyConverter)
        self.converter_mock.convert.side_effect = (
            lambda amount, *_: amount * self.CONVERSION_RATE
        )
        services_container.override(CurrencyConverter, self.converter_mock)


class MockPublishersMixin(ContainerResetOverrideMixin):
    def setUp(self):
        super().setUp()
        self.publisher_mock = MagicMock(Publisher)
        services_container.override(
            TransactionsProducer,
            TransactionsProducer(self.publisher_mock),
        )
        services_container.override(UsersProducer, UsersProducer(self.publisher_mock))


class StopPatchersMixin(TestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(patch.stopall)
