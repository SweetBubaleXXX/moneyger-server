from collections.abc import Iterable
from decimal import Decimal

from rest_framework.response import Response

from moneymanager import services_container

from ..constants import CurrencyCode, TransactionType
from ..services.currency import CurrencyConverter
from .models import Transaction, TransactionCategory


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


def iter_categories_tree(category_id: int):
    yield category_id
    subcategories = TransactionCategory.objects.filter(
        parent_category=category_id
    ).values_list("id", flat=True)
    for child_id in subcategories:
        yield from iter_categories_tree(child_id)


def get_all_subcategories(category: TransactionCategory):
    return TransactionCategory.objects.filter(
        parent_category__in=iter_categories_tree(category.id)
    )


def get_all_transactions(category: TransactionCategory):
    return Transaction.objects.filter(
        category__in=iter_categories_tree(category.id)
    ).select_related("category")
