from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    r"categories",
    views.TransactionCategoryViewSet,
    basename="transaction-category",
)
