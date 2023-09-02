from django.urls import include, path

urlpatterns = [
    path("browsable-api-auth/", include("rest_framework.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("webauthn/", include("djoser.webauthn.urls")),
]
