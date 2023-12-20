from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("users", views.CustomUserViewSet, "users")

urlpatterns = [
    path("browsable-api-auth/", include("rest_framework.urls")),
    path("auth/", include(router.urls)),
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
    path(
        "auth/notifications/",
        views.NotificationsServiceAuthView.as_view(),
        name="notifications-service-token",
    ),
    path("webauthn/", include("djoser.webauthn.urls")),
]
