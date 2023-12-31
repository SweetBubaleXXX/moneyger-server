from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import SimpleTestCase

from moneymanager import services_container

from .services.currency import CurrencyConverter
from .services.notifications.messages import MessagesProducer
from .services.notifications.publishers import Publisher
from .services.notifications.transactions import TransactionsProducer
from .services.notifications.users import UsersProducer, UsersRpcService


class CacheClearMixin(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(cache.clear)


class ContainerResetOverrideMixin(SimpleTestCase):
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
        self.users_rpc_mock = MagicMock(UsersRpcService)
        services_container.override(
            TransactionsProducer,
            TransactionsProducer(self.publisher_mock),
        )
        services_container.override(UsersProducer, UsersProducer(self.publisher_mock))
        services_container.override(
            MessagesProducer,
            MessagesProducer(self.publisher_mock),
        )
        services_container.override(
            UsersRpcService,
            self.users_rpc_mock,
        )


class StopPatchersMixin(SimpleTestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(patch.stopall)
