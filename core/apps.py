from django.apps import AppConfig
from django.conf import settings

from moneymanager import lookup_depth_container, services_container

from .services.currency import CurrencyConverter
from .services.rates_providers import BaseRates


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        services_container.bind(BaseRates, settings.CURRENCY_RATES_PROVIDER)
        services_container[CurrencyConverter] = CurrencyConverter()
        lookup_depth_container[int] = settings.DEFAULT_LOOKUP_DEPTH
