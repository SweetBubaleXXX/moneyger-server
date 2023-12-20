from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .services import (
    create_notifications_service_token,
    unsubscribe_user_from_notifications,
)
from .utils import set_refresh_token_cookie


class CustomJwtObtainPairView(TokenObtainPairView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)
        set_refresh_token_cookie(response)
        return response


class CustomJwtRefreshView(TokenRefreshView):
    @method_decorator(csrf_protect)
    def post(self, request: Request, *args, **kwargs) -> Response:
        request_body = request.data.copy()
        if not request_body.get("refresh"):
            request_body["refresh"] = request.COOKIES.get(
                settings.JWT_REFRESH_TOKEN_COOKIE
            )

        serializer = self.get_serializer(data=request_body)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        response = Response(serializer.validated_data)

        if jwt_settings.ROTATE_REFRESH_TOKENS:
            set_refresh_token_cookie(response)
        return response


class JwtLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        response = Response()
        response.delete_cookie(settings.JWT_REFRESH_TOKEN_COOKIE)
        return response


class CustomUserViewSet(UserViewSet):
    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        unsubscribe_user_from_notifications(instance)


class NotificationsServiceAuth(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs) -> Response:
        access_token = create_notifications_service_token(request.user.id)
        return Response({"access_token": access_token})
