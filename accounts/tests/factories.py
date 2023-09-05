import factory

DEFAULT_ACCOUNT_PASSWORD = "default_password"


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "accounts.Account"

    username = factory.Sequence(lambda n: f"User {n}")
    email = factory.Sequence(lambda n: f"{n}@example.org")
    password = factory.django.Password(DEFAULT_ACCOUNT_PASSWORD)
