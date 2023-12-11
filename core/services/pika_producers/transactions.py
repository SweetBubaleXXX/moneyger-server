from typing import Iterable

from ...transactions.models import Transaction
from .producer import Producer


class TransactionsAddedProducer(Producer):
    def _publish(self, message: Iterable[Transaction]) -> None:
        ...
