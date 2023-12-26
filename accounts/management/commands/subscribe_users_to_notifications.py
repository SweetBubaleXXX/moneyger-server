from django.core.management.base import BaseCommand, CommandError, CommandParser

from accounts.models import Account
from core.services.notifications.users import UsersProducer
from moneymanager import services_container


class Command(BaseCommand):
    help = "Send accounts info to notifications service"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("account_ids", nargs="+", type=int)

    @services_container.inject("users_producer")
    def handle(self, users_producer: UsersProducer, *args, **options) -> str | None:
        for account_id in options["account_ids"]:
            try:
                account = Account.objects.get(id=account_id)
            except Account.DoesNotExist:
                raise CommandError(f"Account with id={account_id} not found")
            users_producer.register_account(account)
        users_producer.send()
        self.stdout.write(self.style.SUCCESS("Success"))
