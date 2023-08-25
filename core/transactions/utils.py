from typing import Generator

from django.db.models import Prefetch

from moneymanager import lookup_depth_container

from .models import Transaction, TransactionCategory


@lookup_depth_container.inject("depth")
def subcategories_lookups(depth: int) -> Generator[str, None, None]:
    for i in range(depth):
        yield "".join(["subcategories", "__subcategories" * i])


@lookup_depth_container.inject("depth")
def subcategories_and_transactions_lookups(depth: int) -> Generator[str, None, None]:
    yield "transactions"
    for lookup in subcategories_lookups(depth - 1):
        yield "".join([lookup, "__transactions"])


def iter_categories_tree(category: TransactionCategory):
    def iter_subcategories(subcategories):
        for category in subcategories:
            yield category.id
            yield from iter_subcategories(category.subcategories.all())

    yield category.id
    prefetch_keys = [
        Prefetch(
            lookup,
            TransactionCategory.objects.all().only("id", "parent_category"),
        )
        for lookup in subcategories_lookups()
    ]
    subcategories = (
        category.subcategories.all()
        .prefetch_related(*prefetch_keys)
        .only("id", "parent_category")
    )
    yield from iter_subcategories(subcategories)


def get_all_subcategories(category: TransactionCategory):
    return TransactionCategory.objects.filter(
        parent_category__in=iter_categories_tree(category)
    )


def get_all_transactions(category: TransactionCategory):
    return Transaction.objects.filter(
        category__in=iter_categories_tree(category)
    ).select_related("category")
