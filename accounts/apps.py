from django.apps import AppConfig
from djoser.signals import user_registered


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self) -> None:
        from . import signals

        user_registered.connect(
            signals.user_registered_receiver,
            dispatch_uid="notification_producer",
        )
