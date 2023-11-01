from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    message_id = serializers.UUIDField()
    user = serializers.CharField()
    is_admin = serializers.BooleanField()
    message_text = serializers.CharField()
