from decimal import Decimal

from iso4217 import Currency

from ..constants import CurrencyChoices


def int_to_decimal(value: int, currency_code: CurrencyChoices) -> Decimal:
    decimal_places = Currency(currency_code).exponent
    return Decimal(value) / 10**decimal_places


def decimal_to_int(value: Decimal, currency_code: CurrencyChoices) -> int:
    decimal_places = Currency(currency_code).exponent
    return int(value * 10**decimal_places)
