from django.urls import path

from .views import ExportCsvView, ExportJsonView, ImportJsonView

urlpatterns = [
    path("import/json/", ImportJsonView.as_view(), name="import-json"),
    path("export/csv/", ExportCsvView.as_view(), name="export-csv"),
    path("export/json/", ExportJsonView.as_view(), name="export-json"),
]
