from django.urls import include, path

urlpatterns = [
    path("", include("core.transactions.urls")),
    path("", include("core.export.urls")),
]
