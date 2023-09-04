from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        response.set_cookie(
            settings.JWT_ACCESS_TOKEN_COOKIE,
            response.data["access"],
            expires=jwt_settings.ACCESS_TOKEN_LIFETIME,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        )
        response.set_cookie(
            settings.JWT_REFRESH_TOKEN_COOKIE,
            response.data["refresh"],
            expires=jwt_settings.REFRESH_TOKEN_LIFETIME,
            samesite=settings.AUTH_COOKIE_SAMESITE,
            httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        )
        return response
