from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from ..transactions.views import BaseViewMixin
from .serializers import CategoryJsonSerializer


class ExportJsonView(BaseViewMixin, GenericAPIView):
    serializer_class = CategoryJsonSerializer

    def get_queryset(self):
        return self.request.user.transactioncategory_set.filter(
            parent_category__isnull=True
        ).prefetch_related("subcategories", "transactions")

    def get(self, request):
        serializer = self.get_serializer(instance=self.get_queryset(), many=True)
        return Response(serializer.data)
