from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from . import utils


class CustomJwtObtainPairView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        utils.set_access_token_cookie(response, response.data["access"])
        utils.set_refresh_token_cookie(response, response.data["refresh"])
        return response


class JwtLogoutView(APIView):
    authentication_classes = []

    def post(self, request):
        response = Response()
        response.delete_cookie(settings.JWT_ACCESS_TOKEN_COOKIE)
        response.delete_cookie(settings.JWT_REFRESH_TOKEN_COOKIE)
        return response
