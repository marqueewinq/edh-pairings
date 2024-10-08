"""
Django settings for pairings project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import json
import os
import typing as ty

import dj_database_url
import judge

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

BASE_URL = os.getenv("BASE_URL", "http://localhost/")

ALLOWED_HOSTS: ty.List[str] = [] + json.loads(os.getenv("ALLOWED_HOSTS", "[]"))
CORS_ALLOWED_ORIGINS = json.loads(os.getenv("CORS_ALLOWED_ORIGINS", "[]"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": "./debug.log",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_auth",
    "constance.backends.database",
    "constance",
    "corsheaders",
    "django_extensions",
    "django_json_widget",
    "tinymce",
    "accounts",
    "frontend",
    "judge",
    "news",
    "pods",
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
]

ROOT_URLCONF = "pairings.urls"

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
                "pairings.context_processors.base_url",
            ]
        },
    }
]

WSGI_APPLICATION = "pairings.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("DATABASE_URL", "sqlite://"),
        conn_max_age=os.getenv("DATABASE_CONNECTION_MAX_AGE", 600),
    )
}

# Authentication
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# JWT

JWT_ALGORITHM = "HS256"
JWT_SECRET_KEY = SECRET_KEY

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "assets"),
    # We do this so that django's collectstatic copies or our bundles to the
    # STATIC_ROOT or syncs them to whatever storage we use.
)

# Authorization

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication"
    ]
}
REST_AUTH_SERIALIZERS = {"LOGIN_SERIALIZER": "accounts.serializers.LoginSerializer"}


# Emails SMTP settings

EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = os.environ["EMAIL_PORT"]
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_FROM = os.environ.get("EMAIL_FROM", "noreply@edh.marqueewinq.xyz")

# Constance

CONSTANCE_ADDITIONAL_FIELDS = {
    "version_select": [
        "django.forms.fields.ChoiceField",
        {
            "widget": "django.forms.Select",
            "choices": judge.get_available_version_choices(),
        },
    ]
}

CONSTANCE_CONFIG = {
    "PRIMARY_SCORE_PER_BUY": (1, "Primary score assigned per player buy", int),
    "SECONDARY_SCORE_PER_BUY": (0, "Secondary score assigned per player buy", int),
    "PRIMARY_WEIGHT": (10.0, "Weight of primary score in pairing algorithm", float),
    "SECONDARY_WEIGHT": (1.0, "Weight of secondary score in pairing algorithm", float),
    "JUDGE_VERSION": (
        "deterministic",
        "Version of pairing algorithm",
        "version_select",
    ),
}

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_CONFIG_FIELDSETS = {
    "Buy Options": ("PRIMARY_SCORE_PER_BUY", "SECONDARY_SCORE_PER_BUY"),
    "Pairing algorithm default config": (
        "JUDGE_VERSION",
        "PRIMARY_WEIGHT",
        "SECONDARY_WEIGHT",
    ),
}

# Donate

DONATE_LINK_RU = os.environ.get("DONATE_LINK_RU")
