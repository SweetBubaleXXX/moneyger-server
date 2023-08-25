from collections.abc import Iterable
from decimal import Decimal

from rest_framework.response import Response

from moneymanager import services_container

from ..constants import CurrencyCode, TransactionType
from ..services.currency import CurrencyConverter
from .models import Transaction


def summary_response(request, transactions):
    total = compute_total(transactions, request.user.default_currency)
    return Response(
        {
            "total": total,
            "currency": request.user.default_currency,
        }
    )


@services_container.inject("currency_converter")
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
