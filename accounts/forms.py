from django.contrib.auth.forms import UserCreationForm

from .models import Account


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Account
        fields = UserCreationForm.Meta.fields + ("email",)
