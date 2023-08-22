from django.urls import path

from .views import ExportCsvView, ExportJsonView

urlpatterns = [
    path("export/csv/", ExportCsvView.as_view(), name="export-csv"),
    path("export/json/", ExportJsonView.as_view(), name="export-json"),
]
