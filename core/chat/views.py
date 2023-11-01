from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MessageSerializer
from .services import MessageCache


class MessagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        messages = MessageCache(settings.DEFAULT_CHAT_GROUP).get_all()
        serializer = MessageSerializer(data=list(messages), many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
