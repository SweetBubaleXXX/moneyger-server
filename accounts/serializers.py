from djoser.serializers import UserSerializer

from .models import Account


class AccountSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = Account
        fields = UserSerializer.Meta.fields + ("default_currency",)
