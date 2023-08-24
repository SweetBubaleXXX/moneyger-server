from celery import shared_task
from django.core.cache import cache

from ..transactions.models import TransactionCategory
from .serializers import CategoryJsonSerializer


@shared_task(bind=True)
def generate_json(self, account_id: int):
    cache.set(f"task_generate_json_{account_id}", self.request.id)
    return CategoryJsonSerializer(
        TransactionCategory.objects.filter(
            account=account_id, parent_category__isnull=True
        ).prefetch_related("subcategories", "transactions"),
        many=True,
    ).data
