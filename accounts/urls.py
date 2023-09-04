from django.urls import include, path

from . import views

urlpatterns = [
    path("browsable-api-auth/", include("rest_framework.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path(
        "auth/jwt/create/",
        views.CustomJwtObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "auth/jwt/logout/",
        views.JwtLogoutView.as_view(),
        name="token_remove_cookie",
    ),
    path("webauthn/", include("djoser.webauthn.urls")),
]
