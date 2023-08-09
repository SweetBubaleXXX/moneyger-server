from decimal import Decimal

from iso4217 import Currency

from ..constants import CurrencyCode
from .rates_providers import BaseRates


def int_to_decimal(value: int, currency_code: CurrencyCode) -> Decimal:
    decimal_places = Currency(currency_code).exponent
    return Decimal(value) / 10**decimal_places


def decimal_to_int(value: Decimal, currency_code: CurrencyCode) -> int:
    decimal_places = Currency(currency_code).exponent
    return round(value * 10**decimal_places)


class CurrencyConverter:
    def __init__(self, rates_provider: BaseRates) -> None:
        self._rates_provider = rates_provider

    @property
    def rates_provider(self) -> BaseRates:
        return self._rates_provider

    @rates_provider.setter
    def rates_provider(self, provider: BaseRates) -> None:
        self._rates_provider = provider

    def convert(
        self, amount: Decimal, cur_from: CurrencyCode, cur_to: CurrencyCode
    ) -> Decimal | int:
        rate = self._rates_provider.get_rate(cur_from, cur_to)
        return round(amount * rate, Currency(cur_to).exponent)
