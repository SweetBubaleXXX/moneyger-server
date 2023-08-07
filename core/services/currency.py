from decimal import Decimal

from iso4217 import Currency

from ..constants import CurrencyCode


def int_to_decimal(value: int, currency_code: CurrencyCode) -> Decimal:
    decimal_places = Currency(currency_code).exponent
    return Decimal(value) / 10**decimal_places


def decimal_to_int(value: Decimal, currency_code: CurrencyCode) -> int:
    decimal_places = Currency(currency_code).exponent
    return int(value * 10**decimal_places)
