from celery import shared_task

from ..transactions.models import TransactionCategory
from .serializers import CategoryJsonSerializer


@shared_task
def generate_json(account_id: int):
    return CategoryJsonSerializer(
        TransactionCategory.objects.filter(
            account=account_id, parent_category__isnull=True
        ).prefetch_related("subcategories", "transactions"),
        many=True,
    ).data
