from django.urls import include, path

from .transactions.router import router as transaction_router

urlpatterns = [
    path("", include(transaction_router.urls)),
]
