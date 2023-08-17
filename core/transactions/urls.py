from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    r"categories",
    views.TransactionCategoryViewSet,
    basename="transaction-category",
)

urlpatterns = [
    path("", include(router.urls)),
    path("transactions/", views.TransactionListView.as_view(), name="transaction-list"),
    path(
        "transactions/<int:pk>/",
        views.TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
]
