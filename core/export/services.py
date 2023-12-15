import csv
from collections import deque
from collections.abc import Iterable
from dataclasses import asdict
from typing import Generator

from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework.response import Response

from ..transactions.models import Transaction
from ..transactions.services import notify_transaction_changes
from .serializers import CategoryJsonSerializer, TransacationCsvSerializer
from .utils import CategoryImportContext, EchoBuffer


def file_timestamp() -> str:
    return timezone.now().strftime(r"%Y_%m_%d-%H_%M_%S")


def csv_generator(transactions: Iterable[Transaction]) -> Generator[str, None, None]:
    fieldnames = (
        "category",
        "transaction_type",
        "currency",
        "amount",
        "transaction_time",
        "comment",
    )
    writer = csv.DictWriter(EchoBuffer(), fieldnames)
    yield writer.writeheader()
    for entry in transactions:
        row = TransacationCsvSerializer(entry).data
        yield writer.writerow(row)


def csv_response(transactions: Iterable[Transaction]) -> StreamingHttpResponse:
    filename = f"Transactions-{file_timestamp()}.csv"
    return StreamingHttpResponse(
        csv_generator(transactions),
        content_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def json_response(result: list) -> Response:
    filename = f"Moneyger-{file_timestamp()}.json"
    return Response(
        result,
        content_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _import_categories(
    categories_import_stack: deque[tuple[list, CategoryImportContext]]
) -> None:
    categories, context = categories_import_stack.pop()
    serializer = CategoryJsonSerializer(
        data=categories,
        context=asdict(context),
        many=True,
    )
    serializer.is_valid(raise_exception=True)
    created_categories = serializer.save()
    for category_data, instance in zip(categories, created_categories):
        categories_import_stack.append(
            (
                category_data["subcategories"],
                CategoryImportContext(
                    account=context.account,
                    parent_category=instance,
                ),
            )
        )


def add_categories_to_account(categories: list, context: CategoryImportContext) -> None:
    categories_import_stack = deque([(categories, context)])
    while categories_import_stack:
        _import_categories(categories_import_stack)
    notify_transaction_changes()
