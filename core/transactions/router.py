from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    r"categories",
    views.TransactionCategoryViewSet,
    basename="transaction-category",
)
router.register(
    r"categories/(?P<category_id>\d+)/add",
    views.ChildTransactionCategoryViewSet,
    basename="transaction-category-add-child",
)
