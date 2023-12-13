import pika
from django.apps import AppConfig
from django.conf import settings

from moneymanager import lookup_depth_container, services_container

from .services.currency import CurrencyConverter
from .services.notifications.publishers import AsyncPublisher, ExchangeConfig
from .services.notifications.transactions import TransactionsProducer
from .services.notifications.users import UsersProducer
from .services.rates_providers import BaseRates


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        notifications_service_connection = pika.URLParameters(
            settings.NOTIFICATIONS_SERVICE_URL
        )

        services_container.bind(BaseRates, settings.CURRENCY_RATES_PROVIDER)
        services_container[CurrencyConverter] = CurrencyConverter()
        services_container[TransactionsProducer] = UsersProducer(
            AsyncPublisher(
                notifications_service_connection,
                ExchangeConfig(
                    name="transactions_exchange",
                    exchange_type="topic",
                    durable=True,
                ),
            )
        )
        services_container[UsersProducer] = UsersProducer(
            AsyncPublisher(
                notifications_service_connection,
                exchange=ExchangeConfig(
                    name="users_exchange",
                    exchange_type="topic",
                    durable=True,
                ),
            )
        )

        lookup_depth_container[int] = settings.DEFAULT_LOOKUP_DEPTH
