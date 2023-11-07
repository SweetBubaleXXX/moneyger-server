"""
ASGI config for moneymanager project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moneymanager.settings")

django_asgi_app = get_asgi_application()

from core.chat.middleware import JWTAuthMiddleware  # noqa: E402
from core.chat.urls import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(
                AuthMiddlewareStack(
                    URLRouter([path("api/", URLRouter(websocket_urlpatterns))]),
                ),
            )
        ),
    }
)
