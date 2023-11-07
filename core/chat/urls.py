from django.urls import path

from . import consumers
from .views import MessagesView

websocket_urlpatterns = [
    path("ws/chat/", consumers.ChatConsumer.as_asgi()),
]

urlpatterns = [
    path("messages/", MessagesView.as_view(), name="chat-messages"),
]
