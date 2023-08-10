from collections.abc import Iterable
from decimal import Decimal

from dependency_injector.wiring import Provide, inject

from moneymanager.containers import Services

from ..constants import CurrencyCode, TransactionType
from ..services.currency import CurrencyConverter
from .models import Transaction, TransactionCategory


@inject
def compute_total(
    transaction_set: Iterable[Transaction],
    output_currency: CurrencyCode,
    currency_converter: CurrencyConverter = Provide[Services.currency_converter],
) -> Decimal:
    total = Decimal(0)
    for transaction in transaction_set:
        amount = transaction.amount_decimal
        if transaction.currency != output_currency:
            amount = currency_converter.convert(
                amount, transaction.currency, output_currency
            )
        if transaction.category.transaction_type == TransactionType.OUTCOME:
            total -= amount
        else:
            total += amount
    return total


def get_all_subcategories(
    category: TransactionCategory,
) -> Iterable[TransactionCategory]:
    subcategories = category.subcategories.all()
    for child in subcategories:
        subcategories = subcategories.union(get_all_subcategories(child))
    return subcategories
