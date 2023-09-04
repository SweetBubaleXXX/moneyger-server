"""
Django settings for moneymanager project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
    "djoser.webauthn",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_filters",
    "colorfield",
    "simple_history",
    "accounts",
    "core",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "accounts.middleware.TokenCookieMiddleware",
]

ROOT_URLCONF = "moneymanager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "moneymanager.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": env.db(),
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.Account"

CACHES = {
    "default": env.cache(default="locmemcache://"),
}

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

INTERNAL_IPS = [
    "127.0.0.1",
]

CORS_ALLOW_ALL_ORIGINS = DEBUG

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

EMAIL_CONFIG = env.email(default="consolemail://")

vars().update(EMAIL_CONFIG)

CELERY_BROKER_URL = env("CELERY_BROKER_URL")

CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CustomJWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

DJOSER = {
    "SEND_ACTIVATION_EMAIL": True,
    "SEND_CONFIRMATION_EMAIL": True,
    "PASSWORD_CHANGED_EMAIL_CONFIRMATION": True,
    "USERNAME_CHANGED_EMAIL_CONFIRMATION": True,
    "ACTIVATION_URL": "actions/activate/{uid}/{token}",
    "PASSWORD_RESET_CONFIRM_URL": "actions/password-reset/{uid}/{token}",
    "USERNAME_RESET_CONFIRM_URL": "actions/username-reset/{uid}/{token}",
    "SERIALIZERS": {
        "user": "accounts.serializers.AccountSerializer",
        "current_user": "accounts.serializers.AccountSerializer",
    },
    "EMAIL": {
        "activation": "accounts.email.CeleryActivationEmail",
        "confirmation": "accounts.email.CeleryConfirmationEmail",
        "password_reset": "accounts.email.CeleryPasswordResetEmail",
        "password_changed_confirmation": "accounts.email.CeleryPasswordChangedConfirmationEmail",
        "username_changed_confirmation": "accounts.email.CeleryUsernameChangedConfirmationEmail",
        "username_reset": "accounts.email.CeleryUsernameResetEmail",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": (
        "Bearer",
        "JWT",
    ),
    "USER_ID_CLAIM": "account_id",
}

SPECTACULAR_SETTINGS = {
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "DISABLE_ERRORS_AND_WARNINGS": True,
    "TITLE": "Moneyger API",
}

JWT_ACCESS_TOKEN_COOKIE = env("JWT_ACCESS_TOKEN_COOKIE", default="access_token")

JWT_REFRESH_TOKEN_COOKIE = env("JWT_REFRESH_TOKEN_COOKIE", default="refresh_token")

AUTH_COOKIE_SECURE = env.bool("AUTH_SECURE_COOKIE", DEBUG)

AUTH_COOKIE_HTTP_ONLY = env.bool("AUTH_COOKIE_HTTP_ONLY", True)

AUTH_COOKIE_SAMESITE = env("AUTH_COOKIE_SAMESITE", default="Lax")

DEFAULT_LOOKUP_DEPTH = 4

CURRENCY_RATES_PROVIDER = env(
    "CURRENCY_RATES_PROVIDER",
    default="core.services.rates_providers.AlfaBankNationalRates",
)

ALFA_BANK_NATIONAL_RATES_URL = env(
    "ALFA_BANK_NATIONAL_RATES_URL",
    default="https://developerhub.alfabank.by:8273/partner/1.0.1/public/nationalRates",
)
