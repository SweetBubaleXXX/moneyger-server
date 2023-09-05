from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.settings import api_settings as jwt_settings


def jwt_cookie_settings():
    return {
        "samesite": settings.AUTH_COOKIE_SAMESITE,
        "httponly": settings.AUTH_COOKIE_HTTP_ONLY,
    }


def set_access_token_cookie(response: Response, value: str):
    response.set_cookie(
        settings.JWT_ACCESS_TOKEN_COOKIE,
        value,
        expires=jwt_settings.ACCESS_TOKEN_LIFETIME,
        **jwt_cookie_settings(),
    )


def set_refresh_token_cookie(response: Response, value: str):
    response.set_cookie(
        settings.JWT_REFRESH_TOKEN_COOKIE,
        value,
        expires=jwt_settings.REFRESH_TOKEN_LIFETIME,
        **jwt_cookie_settings(),
    )
