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
        "auth/jwt/refresh/",
        views.CustomJwtRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "auth/jwt/logout/",
        views.JwtLogoutView.as_view(),
        name="token_logout",
    ),
    path("webauthn/", include("djoser.webauthn.urls")),
]
