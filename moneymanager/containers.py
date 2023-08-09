from dependency_injector import containers, providers
from django.conf import settings

from core.services.currency import CurrencyConverter
from core.services.rates_providers import BaseRates


class CurrencyRatesProvider(providers.Factory):
    provided_type = BaseRates


class Services(containers.DeclarativeContainer):
    currency_rates_provider = CurrencyRatesProvider(settings.CURRENCY_RATES_PROVIDER)
    currency_converter = providers.Factory(
        CurrencyConverter, rates_provider=currency_rates_provider
    )
