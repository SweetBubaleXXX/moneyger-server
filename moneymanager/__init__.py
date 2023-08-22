from .celery import app as celery_app
from .containers import Services

__all__ = ("celery_app",)

services_container = Services()
