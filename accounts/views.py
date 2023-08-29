from knox.views import LoginView as KnoxLoginView
from rest_framework.authentication import BasicAuthentication, SessionAuthentication


class LoginView(KnoxLoginView):
    authentication_classes = (BasicAuthentication, SessionAuthentication)

    def get_token_ttl(self):
        return self.request.user.session_ttl
