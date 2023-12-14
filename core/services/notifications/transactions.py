import json
from typing import TYPE_CHECKING, Collection, Iterable, Literal, Self, TypedDict

from core.constants import CurrencyCode
from moneymanager import services_container

from ..currency import CurrencyConverter
from .producer import Producer
from .publishers import Message

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
        transaction_time=transaction.transaction_time,
    )


class TransactionsProducer(Producer):
    def delete_transactions(self, transactions: Collection[int]) -> Self:
        self.publisher.add_message(
            Message(
                routing_key="transaction.event.deleted",
                body=json.dumps(transactions),
            )
        )
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
        self.publisher.add_message(
            Message(
                routing_key,
                body=json.dumps(serialized_transactions),
            )
        )
        return self
