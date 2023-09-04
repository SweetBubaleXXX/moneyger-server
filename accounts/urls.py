from django.urls import include, path

from .views import CustomTokenObtainPairView

urlpatterns = [
    path("browsable-api-auth/", include("rest_framework.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "auth/jwt/create/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("webauthn/", include("djoser.webauthn.urls")),
]
