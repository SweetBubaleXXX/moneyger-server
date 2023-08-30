from celery.result import AsyncResult
from django.core.cache import cache
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from ..transactions.filters import TransactionFilter
from ..transactions.views import BaseViewMixin
from .services import csv_response, json_response
from .tasks import generate_json


class ExportCsvView(BaseViewMixin, GenericAPIView):
    filterset_class = TransactionFilter

    def get_queryset(self):
        return self.request.user.transaction_set.all().select_related("category")

    def get(self, request):
        return csv_response(self.filter_queryset(self.get_queryset()))


class ExportJsonView(BaseViewMixin, APIView):
    def get(self, request):
        task_name = f"task_generate_json_{request.user.id}"
        task_id = cache.get(task_name)
        if not task_id:
            task = generate_json.delay(request.user.id)
            cache.set(task_name, task.id)
            return Response(status=status.HTTP_202_ACCEPTED)
        task = AsyncResult(task_id)
        if task.ready():
            result = task.result
            failed = task.failed()
            cache.delete(task_name)
            task.forget()
            if failed:
                raise result
            return json_response(result)
        return Response(status=status.HTTP_202_ACCEPTED)
