from iso4217 import Currency

from ...constants import CurrencyCode


def test_currency_metadata():
    for currency in CurrencyCode:
        Currency(currency)
