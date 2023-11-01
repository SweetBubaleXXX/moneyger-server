from channels.routing import URLRouter
from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat/", consumers.ChatConsumer.as_asgi()),
]

websocket_urls = [path("api/", URLRouter(websocket_urlpatterns))]
