import factory

from ...constants import CurrencyChoices, TransactionType
from ..models import Transaction, TransactionCategory

DEFAULT_ACCOUNT_PASSWORD = "default_password"


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.Account"

    username = factory.Faker("first_name")
    password = factory.django.Password(DEFAULT_ACCOUNT_PASSWORD)


class TransactionCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TransactionCategory

    account = factory.SubFactory(AccountFactory)
    transaction_type = factory.Iterator(TransactionType)
    parent_category = factory.SubFactory(
        "core.transactions.factories.TransactionCategoryFactory",
        transaction_type=factory.SelfAttribute("..transaction_type"),
    )
    name = factory.sequence(lambda n: "Category %d" % n)
    color = factory.Faker("color")


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    category = factory.SubFactory(TransactionCategoryFactory)
    amount = factory.Faker("pyint")
    currency = factory.Iterator(CurrencyChoices)
    comment = factory.Faker("text", max_nb_chars=30)
    transaction_time = factory.Faker("date_time")
