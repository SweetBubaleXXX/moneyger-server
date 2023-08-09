from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import (
    TransactionCategoryFilter,
    TransactionFilter,
    TransactionSummaryFilter,
)
from .permissions import IsOwnAccount
from .serializers import (
    TransactionCategorySerializer,
    TransactionCategoryUpdateSerializer,
    TransactionSerializer,
    TransactionUpdateSerializer,
)
from .services import compute_total


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
        subcategories = self.get_object().subcategories.all()
        page = self.paginate_queryset(subcategories)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
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

    @action(
        serializer_class=TransactionSerializer,
        filterset_class=None,
        detail=True,
        methods=("get",),
        url_name="transactions",
    )
    def transactions(self, request, category_id=None):
        transactions = self.get_object().transactions.all()
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @transactions.mapping.post
    def add_transaction(self, request, category_id=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            account=request.user,
            category=self.get_object(),
        )
        return Response(serializer.data)


class TransactionViewMixin:
    serializer_class = TransactionSerializer
    permission_classes = (IsOwnAccount,)

    def get_queryset(self):
        return self.request.user.transaction_set.all()


class TransactionListView(TransactionViewMixin, generics.ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TransactionFilter


class TransactionDetailView(
    TransactionViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = TransactionUpdateSerializer


class TransactionSummaryView(TransactionViewMixin, generics.GenericAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TransactionSummaryFilter

    def get(self, request, format=None):
        transactions = self.filter_queryset(self.get_queryset())
        total = compute_total(transactions, request.user.default_currency)
        return Response(
            {
                "total": total,
                "currency": request.user.default_currency,
            }
        )
