from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import TransactionCategoryFilter
from .permissions import IsOwnAccount
from .serializers import (
    TransactionCategorySerializer,
    TransactionCategoryUpdateSerializer,
)


class TransactionCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionCategorySerializer
    permission_classes = (IsOwnAccount,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TransactionCategoryFilter
    lookup_url_kwarg = "category_id"

    def get_serializer_class(self):
        if self.action in ("update", "partial_update", "add_subcategory"):
            return TransactionCategoryUpdateSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.request.user.transactioncategory_set.all()

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)

    @action(
        detail=True,
        methods=("get",),
        url_name="subcategories",
    )
    def subcategories(self, request, category_id=None):
        subcategories = self.get_object().subcategories
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)

    @subcategories.mapping.post
    def add_subcategory(self, request, category_id=None):
        parent_category = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            account=request.user,
            parent_category=parent_category,
            transaction_type=parent_category.transaction_type,
        )
        return Response(serializer.data)
