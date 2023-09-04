from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError


class TokenCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get("access")
        refresh_token = request.COOKIES.get("refresh")
        try:
            decoded_token = AccessToken(access_token, False)
            if decoded_token.check_exp():
                decoded_refresh_token = RefreshToken(refresh_token)
                access_token = decoded_refresh_token.access_token
        except TokenError:
            pass
        finally:
            if access_token:
                request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
        response = self.get_response(request)
        if access_token:
            response.set_cookie("access", access_token, httponly=True)
        return response

    # def process_view(self, request, view_func, view_args, view_kwargs):
    #     ...
