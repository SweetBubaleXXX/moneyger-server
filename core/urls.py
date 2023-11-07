from django.urls import include, path

urlpatterns = [
    path("", include("core.transactions.urls")),
    path("", include("core.export.urls")),
    path("chat/", include("core.chat.urls")),
]
