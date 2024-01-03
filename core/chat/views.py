from operator import itemgetter

from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.messages import MessageCache
from .serializers import MessageSerializer


class MessagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        messages = MessageCache(settings.DEFAULT_CHAT_GROUP).get_all()
        sorted_messages = sorted(messages, key=itemgetter("timestamp"))
        serializer = MessageSerializer(data=list(sorted_messages), many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
