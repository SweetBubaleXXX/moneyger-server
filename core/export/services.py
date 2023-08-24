import csv
from collections.abc import Iterable
from typing import Generator, TypeVar

from django.http import StreamingHttpResponse
from django.utils import timezone
from rest_framework.response import Response

from ..transactions.models import Transaction
from .serializers import TransacationCsvSerializer

T = TypeVar("T")


class _EchoBuffer:
    def write(self, value: T) -> T:
        return value


def csv_generator(transactions: Iterable[Transaction]) -> Generator[str, None, None]:
    fieldnames = (
        "category",
        "transaction_type",
        "currency",
        "amount",
        "transaction_time",
        "comment",
    )
    writer = csv.DictWriter(_EchoBuffer(), fieldnames)
    yield writer.writeheader()
    for entry in transactions:
        row = TransacationCsvSerializer(entry).data
        yield writer.writerow(row)


def file_timestamp() -> str:
    return timezone.now().strftime(r"%Y_%m_%d-%H_%M_%S")


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
