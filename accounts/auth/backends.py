from django.conf import settings
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request: Request):
        raw_token = request.COOKIES.get(settings.JWT_ACCESS_TOKEN_COOKIE)
        if not raw_token:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def authenticate_header(self, request):
        pass
