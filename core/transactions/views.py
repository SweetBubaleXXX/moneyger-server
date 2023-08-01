from functools import cache

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

    def get_serializer_class(self):
        if self.action in ("update", "partial_update", "add_child_category"):
            return TransactionCategoryUpdateSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.request.user.transactioncategory_set.all()

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)

    @action(
        detail=True,
        methods=("get",),
        url_name="children",
    )
    def child_categories(self, request, category_id=None):
        child_categories = self.get_object().child_categories
        serializer = self.get_serializer(child_categories, many=True)
        return Response(serializer.data)

    @child_categories.mapping.post
    def add_child_category(self, request, category_id=None):
        parent_category = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            account=request.user,
            parent_category=parent_category,
            transaction_type=parent_category.transaction_type,
        )
        return Response(serializer.data)
