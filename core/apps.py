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
from .services.notifications.publishers import AsyncPublisher, ExchangeConfig
from .services.notifications.transactions import TransactionsProducer
from .services.notifications.users import UsersProducer
from .services.rates_providers import BaseRates


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        if settings.NOTIFICATIONS_SERVICE_URL:
            notifications_service_config[connection.Parameters] = pika.URLParameters(
                settings.NOTIFICATIONS_SERVICE_URL
            )
        else:
            notifications_service_config[
                connection.Parameters
            ] = pika.ConnectionParameters()

        services_container.bind(BaseRates, settings.CURRENCY_RATES_PROVIDER)
        services_container[CurrencyConverter] = CurrencyConverter()
        services_container[TransactionsProducer] = TransactionsProducer(
            AsyncPublisher(
                exchange=ExchangeConfig(
                    name="transactions_exchange",
                    exchange_type="topic",
                    durable=True,
                ),
            )
        )
        services_container[UsersProducer] = UsersProducer(
            AsyncPublisher(
                exchange=ExchangeConfig(
                    name="users_exchange",
                    exchange_type="topic",
                    durable=True,
                ),
            )
        )

        lookup_depth_container[int] = settings.DEFAULT_LOOKUP_DEPTH
