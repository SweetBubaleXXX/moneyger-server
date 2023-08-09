from django.apps import AppConfig

from moneymanager import services_container


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        services_container.wire(modules=[".transactions.services"])
