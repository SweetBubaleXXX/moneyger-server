from knox.views import LoginView as KnoxLoginView
from rest_framework.authentication import BaseAuthentication


class LoginView(KnoxLoginView):
    authentication_classes = (BaseAuthentication,)
