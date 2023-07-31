from functools import lru_cache

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets

from .models import TransactionCategory
from .permissions import IsOwnAccount
from .serializers import (
    TransactionCategorySerializer,
    TransactionCategoryUpdateSerializer,
)


class TransactionCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionCategorySerializer
    permission_classes = (IsOwnAccount,)
    lookup_url_kwarg = "category_id"

    def get_queryset(self):
        return self.request.user.transactioncategory_set.all()

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return TransactionCategoryUpdateSerializer
        return self.serializer_class


class ChildTransactionCategoryViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = TransactionCategoryUpdateSerializer
    permission_classes = (IsOwnAccount,)

    @lru_cache(maxsize=1)
    def get_object(self):
        obj = get_object_or_404(TransactionCategory, pk=self.kwargs["category_id"])
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        parent_category = self.get_object()
        serializer.save(
            account=self.request.user,
            parent_category=parent_category,
            transaction_type=parent_category.transaction_type,
        )
