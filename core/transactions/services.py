from collections.abc import Iterable
from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response

from moneymanager import services_container

from ..transactions.filters import TransactionFilter
from ..transactions.serializers import SummarySerializer, StatsSerializer
from ..constants import CurrencyCode, TransactionType
from ..services.currency import CurrencyConverter
from . import utils
from .models import Transaction


def _response_serializer_or_error(serializer):
    if not serializer.is_valid():
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.data)


def summary_response(request, transactions):
    total = compute_total(transactions, request.user.default_currency)
    serializer = SummarySerializer(
        data={
            "total": total,
            "currency": request.user.default_currency,
        }
    )
    return _response_serializer_or_error(serializer)


def stats_response(request, categories):
    categories_summary = []
    for category in categories:
        transactions = TransactionFilter(
            request.query_params, utils.get_all_transactions(category)
        ).qs
        category_total = compute_total(transactions, request.user.default_currency)
        categories_summary.append(
            {
                "id": category.id,
                "total": category_total,
            }
        )
    total = sum(map(lambda category: category["total"], categories_summary))
    serializer = StatsSerializer(
        data={
            "total": total,
            "currency": request.user.default_currency,
            "categories": categories_summary,
        }
    )
    return _response_serializer_or_error(serializer)


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
