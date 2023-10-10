from dataclasses import dataclass
from typing import NamedTuple, TypeVar

from accounts.models import Account

from ..transactions.models import TransactionCategory

T = TypeVar("T")


class EchoBuffer:
    def write(self, value: T) -> T:
        return value


@dataclass
class CategoryImportContext:
    account: Account
    parent_category: TransactionCategory | None = None


class ParsedCategory(NamedTuple):
    instance: TransactionCategory
    transactions: list[dict]
