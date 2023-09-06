from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.settings import api_settings as jwt_settings

from .utils import set_refresh_token_cookie


class CustomJwtObtainPairView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        set_refresh_token_cookie(response)
        return response


class CustomJwtRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        if not request.data.get("refresh"):
            request.data["refresh"] = request.COOKIES.get(
                settings.JWT_REFRESH_TOKEN_COOKIE
            )
        response = super().post(request, *args, **kwargs)
        if jwt_settings.ROTATE_REFRESH_TOKENS:
            set_refresh_token_cookie(response)
        return response
