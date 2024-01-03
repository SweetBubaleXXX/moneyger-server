from django.core.management.base import BaseCommand, CommandParser

from core.services.notifications.transactions import TransactionsProducer
from core.transactions.models import Transaction
from moneymanager import services_container


class Command(BaseCommand):
    help = "Send transactions to notifications service"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("account_ids", nargs="+", type=int)

    @services_container.inject("transactions_producer")
    def handle(
        self,
        transactions_producer: TransactionsProducer,
        *args,
        **options,
    ) -> str | None:
        account_ids = options["account_ids"]
        transactions = Transaction.objects.filter(account_id__in=account_ids)
        transactions_producer.add_transactions(transactions).send()
        transaction_count = len(transactions)
        self.stdout.write(self.style.SUCCESS(f"Sent {transaction_count} transactions"))
