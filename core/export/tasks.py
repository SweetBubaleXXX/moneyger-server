from celery import shared_task
from django.core.cache import cache
from rest_framework.response import Response

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


def json_response(account_id: int):
    return Response(
        generate_json(account_id),
        content_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="Moneyger.json"'},
    )
