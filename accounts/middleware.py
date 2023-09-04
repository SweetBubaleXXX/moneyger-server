from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError


class TokenCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get("access_token")
        refresh_token = request.COOKIES.get("refresh_token")
        try:
            decoded_token = AccessToken(access_token, verify=False)
            if decoded_token.check_exp():
                decoded_refresh_token = RefreshToken(refresh_token)
                request.COOKIES["access_token"] = decoded_refresh_token.access_token
        except TokenError:
            pass
        return self.get_response(request)
