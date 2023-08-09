from collections.abc import Iterable
from decimal import Decimal

from ..constants import CurrencyCode, TransactionType
from ..services.currency import CurrencyConverter
from .models import Transaction


def compute_total(
    transaction_set: Iterable[Transaction],
    output_currency: CurrencyCode,
    currency_converter: CurrencyConverter,
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
