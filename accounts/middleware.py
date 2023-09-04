from rest_framework_simplejwt.tokens import AccessToken, RefreshToken, TokenError


class JwtRefreshCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get("access_token")
        try:
            decoded_token = AccessToken(access_token, verify=False)
            if self._access_token_expired(decoded_token):
                return self._refresh_token(request)
        except TokenError:
            pass
        return self.get_response(request)

    def _refresh_token(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        decoded_refresh_token = RefreshToken(refresh_token)
        new_access_token = str(decoded_refresh_token.access_token)
        request.COOKIES["access_token"] = new_access_token
        response = self.get_response(request)
        response.set_cookie("access_token", new_access_token)
        return response

    def _access_token_expired(self, token: AccessToken) -> bool:
        try:
            token.check_exp()
        except TokenError:
            return True
        return False
