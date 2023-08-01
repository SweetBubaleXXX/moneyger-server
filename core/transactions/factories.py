import factory

from ..constants import TransactionType
from .models import TransactionCategory

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
    transaction_type = TransactionType.OUTCOME[0]
    parent_category = factory.SubFactory(
        "core.transactions.factories.TransactionCategoryFactory",
        transaction_type=factory.SelfAttribute("..transaction_type"),
    )
    name = factory.sequence(lambda n: "Category %d" % n)
    color = factory.Faker("color")
