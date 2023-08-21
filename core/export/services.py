import csv
import json
from collections.abc import Iterable, Mapping
from typing import TypeVar

from django.http import StreamingHttpResponse

from ..transactions.models import Transaction
from .serializers import TransacationExportSerializer

T = TypeVar("T")


class _EchoBuffer:
    def write(self, value: T) -> T:
        return value


def csv_generator(transactions: Iterable[Transaction]):
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
        row = TransacationExportSerializer(entry).data
        yield writer.writerow(row)


def csv_response(transactions: Iterable[Transaction]):
    return StreamingHttpResponse(
        csv_generator(transactions),
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="transactions.csv"'},
    )