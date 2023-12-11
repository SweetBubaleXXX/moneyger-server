import json
from typing import Collection, Iterable, Literal, TypedDict

from constants import CurrencyCode
from transactions.models import Transaction

from moneymanager import services_container

from ..currency import CurrencyConverter
from .producer import Producer


class _SerializedTransaction(TypedDict):
    transaction_id: int
    account_id: int
    transaction_type: Literal["IN", "OUT"]
    amount: str
    transaction_time: str


@services_container.inject("currency_converter")
def _serialize_transaction(
    transaction: Transaction,
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
    def add_transactions(self, transactions: Iterable[Transaction]) -> None:
        self._send_transactions("transaction.event.created", transactions)

    def update_transactions(self, transactions: Iterable[Transaction]) -> None:
        self._send_transactions("transaction.event.updated", transactions)

    def delete_transactions(self, transactions: Collection[int]) -> None:
        self.publish("transaction.event.deleted", json.dumps(transactions))

    def _send_transactions(
        self,
        routing_key: str,
        transactions: Iterable[Transaction],
    ) -> None:
        serialized_transactions = list(map(_serialize_transaction, transactions))
        self.publish(routing_key, json.dumps(serialized_transactions))
