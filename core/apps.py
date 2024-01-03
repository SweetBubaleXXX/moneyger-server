import pika
from django.apps import AppConfig
from django.conf import settings
from pika import connection

from moneymanager import (
    lookup_depth_container,
    notifications_service_config,
    services_container,
)

from .services.currency import CurrencyConverter
from .services.notifications.messages import MessagesProducer
from .services.notifications.publishers import AsynchronousPublisher, ExchangeConfig
from .services.notifications.rpc import RpcClientFactory
from .services.notifications.transactions import TransactionsProducer
from .services.notifications.users import UsersProducer, UsersRpcService
from .services.rates_providers import BaseRates


def _wire_containers():
    if settings.RABBITMQ_URL:
        notifications_service_config[connection.Parameters] = pika.URLParameters(
            settings.RABBITMQ_URL
        )
    else:
        notifications_service_config[
            connection.Parameters
        ] = pika.ConnectionParameters()

    users_exchange = ExchangeConfig(
        name="users_exchange",
        exchange_type="topic",
        durable=True,
    )

    services_container.bind(BaseRates, settings.CURRENCY_RATES_PROVIDER)
    services_container[CurrencyConverter] = CurrencyConverter()
    services_container[TransactionsProducer] = TransactionsProducer(
        AsynchronousPublisher(
            exchange=ExchangeConfig(
                name="transactions_exchange",
                exchange_type="topic",
                durable=True,
            ),
        )
    )
    services_container[UsersProducer] = UsersProducer(
        AsynchronousPublisher(exchange=users_exchange)
    )
    services_container[MessagesProducer] = MessagesProducer(
        AsynchronousPublisher(
            exchange=ExchangeConfig(
                name="messages_exchange",
                exchange_type="topic",
                durable=True,
            )
        )
    )
    services_container[UsersRpcService] = UsersRpcService(
        RpcClientFactory(exchange=users_exchange)
    )

    lookup_depth_container[int] = settings.DEFAULT_LOOKUP_DEPTH


def _connect_signal_receivers():
    from .transactions import signals  # noqa


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        _wire_containers()
        _connect_signal_receivers()
