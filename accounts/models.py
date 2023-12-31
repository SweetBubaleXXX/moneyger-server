from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from core.constants import CurrencyCode


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("Username required")
        if not email:
            raise ValueError("Email required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        user = self.create_user(username, email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Account(AbstractUser):
    email = models.EmailField(unique=True, null=False, blank=False)
    default_currency = models.CharField(
        max_length=3, choices=CurrencyCode.choices, default=CurrencyCode.USD
    )

    REQUIRED_FIELDS = ("email",)

    objects = CustomUserManager()
