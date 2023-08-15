from importlib import import_module

from django.conf import settings

from core.services.currency import CurrencyConverter
from core.services.rates_providers import BaseRates

from .utils import InjectionContainer

currency_rates_provider = import_module(settings.CURRENCY_RATES_PROVIDER)
services_container = InjectionContainer()
services_container[BaseRates] = import_module(settings.CURRENCY_RATES_PROVIDER)
services_container[CurrencyConverter] = CurrencyConverter()

