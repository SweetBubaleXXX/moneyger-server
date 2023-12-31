from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services, utils
from .filters import TransactionCategoryFilter, TransactionFilter
from .permissions import IsOwnAccount
from .serializers import (
    TransactionCategorySerializer,
    TransactionCategoryUpdateSerializer,
    TransactionSerializer,
    TransactionUpdateSerializer,
)
from .services import notify_transaction_changes


class BaseViewMixin:
    permission_classes = (IsOwnAccount,)
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    )


class TransactionCategoryViewSet(BaseViewMixin, viewsets.ModelViewSet):
    serializer_class = TransactionCategorySerializer
    filterset_class = TransactionCategoryFilter
    search_fields = ("name",)
    ordering_fields = ("display_order", "name")
    ordering = ("display_order",)
    lookup_url_kwarg = "category_id"

    def get_serializer_class(self):
        if self.action in ("update", "partial_update", "add_subcategory"):
            return TransactionCategoryUpdateSerializer
        return self.serializer_class

    def get_queryset(self):
        return self.request.user.transactioncategory_set.all()

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        notify_transaction_changes()

    def paginate_queryset(self, queryset):
        if "all" in self.request.query_params:
            return None
        return super().paginate_queryset(queryset)

    @action(
        detail=False,
        methods=("get",),
        url_name="stats",
    )
    def stats(self, request):
        categories = self.filter_queryset(self.get_queryset())
        if "parent_category" not in request.query_params:
            categories = categories.filter(parent_category__isnull=True)
        return services.stats_response(request, categories)

    @action(
        detail=True,
        methods=("get",),
        url_name="subcategories",
    )
    def subcategories(self, request, category_id=None):
        subcategories = utils.get_all_subcategories(self.get_object())
        return self._paginated_response(subcategories.order_by("-display_order"))

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
        transactions = utils.get_all_transactions(self.get_object())
        return self._paginated_response(transactions.order_by("-transaction_time"))

    @transactions.mapping.post
    def add_transaction(self, request, category_id=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            account=request.user,
            category=self.get_object(),
        )
        notify_transaction_changes()
        return Response(serializer.data)

    @action(
        detail=True,
        methods=("get",),
        url_name="summary",
    )
    def summary(self, request, category_id=None):
        transactions = TransactionFilter(
            request.query_params, utils.get_all_transactions(self.get_object())
        ).qs
        return services.summary_response(request, transactions)

    def _paginated_response(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TransactionViewMixin(BaseViewMixin):
    serializer_class = TransactionSerializer
    filterset_class = TransactionFilter
    search_fields = ("comment",)
    ordering_fields = ("transaction_time",)
    ordering = ("-transaction_time",)

    def get_queryset(self):
        return self.request.user.transaction_set.select_related("category").all()


class TransactionListView(TransactionViewMixin, generics.ListAPIView):
    pass


class TransactionDetailView(
    TransactionViewMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = TransactionUpdateSerializer

    def perform_update(self, serializer):
        super().perform_update(serializer)
        notify_transaction_changes()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        notify_transaction_changes()


class TransactionSummaryView(TransactionViewMixin, generics.GenericAPIView):
    def get(self, request):
        transactions = self.filter_queryset(self.get_queryset())
        return services.summary_response(request, transactions)
