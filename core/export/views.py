from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from ..transactions.filters import TransactionFilter
from ..transactions.views import BaseViewMixin
from .serializers import CategoryJsonSerializer
from .services import csv_response


class ExportCsvView(BaseViewMixin, GenericAPIView):
    filterset_class = TransactionFilter

    def get_queryset(self):
        return self.request.user.transaction_set.all().select_related("category")

    def get(self, request):
        return csv_response(self.filter_queryset(self.get_queryset()))


class ExportJsonView(BaseViewMixin, GenericAPIView):
    serializer_class = CategoryJsonSerializer

    def get_queryset(self):
        return self.request.user.transactioncategory_set.filter(
            parent_category__isnull=True
        ).prefetch_related("subcategories", "transactions")

    def get(self, request):
        serializer = self.get_serializer(instance=self.get_queryset(), many=True)
        return Response(serializer.data)
