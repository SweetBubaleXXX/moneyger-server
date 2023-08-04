from iso4217 import Currency

from ...constants import CurrencyChoices


def test_currency_metadata():
    for currency in CurrencyChoices:
        Currency(currency)
