from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from .transactions import urls as transaction_urls

schema_view = get_schema_view(
    openapi.Info(
        title="Moneyger",
        default_version="v1",
        license=openapi.License(name="MIT License"),
    ),
    public=True,
)

urlpatterns = [
    path("swagger<format>/", schema_view.without_ui(), name="schema-json"),
    path(
        "swagger/",
        schema_view.with_ui("swagger"),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc"), name="schema-redoc"),
    *transaction_urls.urlpatterns,
]
