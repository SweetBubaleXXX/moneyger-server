import json
import threading
from collections import defaultdict
from operator import itemgetter
from typing import TYPE_CHECKING, Collection, Iterable, Literal, Self, TypedDict

from core.constants import CurrencyCode
from core.services.notifications.publishers import Publisher
from moneymanager import services_container

from ..currency import CurrencyConverter
from .producer import Producer
from .publishers import PublisherMessage

if TYPE_CHECKING:
    from core.transactions.models import Transaction


class _SerializedTransaction(TypedDict):
    transaction_id: int
    account_id: int
    transaction_type: Literal["IN", "OUT"]
    amount: str
    transaction_time: str


@services_container.inject("currency_converter")
def _serialize_transaction(
    transaction: "Transaction",
    currency_converter: CurrencyConverter,
) -> _SerializedTransaction:
    usd_amount = currency_converter.convert(
        transaction.amount_decimal,
        transaction.currency,
        CurrencyCode.USD,
    )
    return _SerializedTransaction(
        transaction_id=transaction.id,
        account_id=transaction.account.id,
        transaction_type=transaction.category.transaction_type,
        amount=str(usd_amount),
        transaction_time=transaction.transaction_time.isoformat(),
    )


class TransactionsProducer(Producer):
    def __init__(self, publisher: Publisher) -> None:
        super().__init__(publisher)
        self.buffer_queues: dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()

    def delete_transactions(self, transactions: Collection[int]) -> Self:
        with self._lock:
            self.buffer_queues["transaction.event.deleted"].extend(transactions)
        return self

    def add_transactions(self, transactions: Iterable["Transaction"]) -> Self:
        return self._add_transactions("transaction.event.created", transactions)

    def update_transactions(self, transactions: Iterable["Transaction"]) -> Self:
        return self._add_transactions("transaction.event.updated", transactions)

    def _add_transactions(
        self,
        routing_key: str,
        transactions: Iterable["Transaction"],
    ) -> Self:
        serialized_transactions = list(map(_serialize_transaction, transactions))
        with self._lock:
            self.buffer_queues[routing_key].extend(serialized_transactions)
        return self

    def send(self) -> None:
        with self._lock:
            non_empty_queues = filter(itemgetter(1), self.buffer_queues.items())
            for routing_key, transactions in non_empty_queues:
                self.publisher.add_message(
                    PublisherMessage(routing_key, json.dumps(transactions)),
                )
            self.buffer_queues.clear()
        super().send()
