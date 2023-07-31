from django.urls import include, path
from rest_framework import routers

from .transactions.views import (
    ChildTransactionCategoryViewSet,
    TransactionCategoryViewSet,
)

transaction_router = routers.DefaultRouter()
transaction_router.register(
    r"categories",
    TransactionCategoryViewSet,
    basename="transaction-category",
)
transaction_router.register(
    r"categories/(?P<category_id>\d+)/add",
    ChildTransactionCategoryViewSet,
    basename="transaction-category-add-child",
)

urlpatterns = [
    path("", include(transaction_router.urls)),
]
