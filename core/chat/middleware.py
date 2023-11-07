from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken


class JWTAuthMiddleware:
    User = get_user_model()

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            jwt_token_list = parse_qs(scope["query_string"].decode("utf8")).get(
                "token", None
            )
            assert jwt_token_list
            jwt_token = jwt_token_list[0]
            validated_token = AccessToken(jwt_token)
            user_id = self.get_user_credentials(validated_token)
            scope["user"] = await self.get_user(user_id)
        except (AssertionError, TokenError, self.User.DoesNotExist):
            scope["user"] = AnonymousUser()
        return await self.app(scope, receive, send)

    def get_user_credentials(self, payload: AccessToken):
        user_id = payload[api_settings.USER_ID_CLAIM]
        return user_id

    @database_sync_to_async
    def get_user(self, user_id):
        return self.User.objects.get(id=user_id)
