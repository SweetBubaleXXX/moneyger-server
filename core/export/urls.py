from django.urls import path

from .views import ExportJsonView

urlpatterns = [
    path("export/json/", ExportJsonView.as_view(), name="export-json"),
]
