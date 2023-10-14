from django.urls import include, path

urlpatterns = [
    path("api/", include("core.transactions.urls")),
    path("api/", include("core.export.urls")),
]
