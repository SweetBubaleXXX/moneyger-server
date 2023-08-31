import factory
from django.utils import timezone

from accounts.factories import AccountFactory, DEFAULT_ACCOUNT_PASSWORD

from ...constants import CurrencyCode, TransactionType
from ..models import Transaction, TransactionCategory


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.Account"

    username = factory.Sequence(lambda n: f"User {n}")
    email = factory.Sequence(lambda n: f"{n}@example.org")
    password = factory.django.Password(DEFAULT_ACCOUNT_PASSWORD)


class TransactionCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TransactionCategory

    account = factory.SubFactory(AccountFactory)
    transaction_type = factory.Iterator(TransactionType)
    parent_category = factory.SubFactory(
        "core.transactions.tests.factories.TransactionCategoryFactory",
        transaction_type=factory.SelfAttribute("..transaction_type"),
    )
    name = factory.Sequence(lambda n: f"Category {n}")
    color = factory.Faker("color")


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    category = factory.SubFactory(TransactionCategoryFactory)
    amount = factory.Faker("pyint")
    currency = factory.Iterator(CurrencyCode)
    comment = factory.Faker("text", max_nb_chars=30)
    transaction_time = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )
