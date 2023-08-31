from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm
from .models import Account


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = Account
    list_display = ("username", "email", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Preferences",
            {
                "fields": ("default_currency",),
            },
        ),
    )
    add_fieldsets = [
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    ]


admin.site.register(Account, CustomUserAdmin)
