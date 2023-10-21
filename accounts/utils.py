from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings as jwt_settings


def set_refresh_token_cookie(response: Response):
    response.set_cookie(
        settings.JWT_REFRESH_TOKEN_COOKIE,
        response.data["refresh"],
        expires=jwt_settings.REFRESH_TOKEN_LIFETIME,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        httponly=settings.AUTH_COOKIE_HTTP_ONLY,
        secure=settings.AUTH_COOKIE_SECURE,
    )
