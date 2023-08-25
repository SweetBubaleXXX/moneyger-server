from celery import shared_task

from ..transactions.models import TransactionCategory
from ..transactions.utils import subcategories_and_transactions_lookups
from .serializers import CategoryJsonSerializer


@shared_task
def generate_json(account_id: int):
    lookups = tuple(subcategories_and_transactions_lookups())
    queryset = TransactionCategory.objects.filter(
        account=account_id, parent_category__isnull=True
    ).prefetch_related(*lookups)
    return CategoryJsonSerializer(
        queryset,
        many=True,
    ).data
