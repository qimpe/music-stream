import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

print(f"{BASE_DIR=}")

SECRET_KEY = os.getenv("APP_KEY")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tailwind",
    "minio_storage",
    "django_browser_reload",
    "apps.theme",
    "apps.oauth",
    "apps.music",
    "apps.users",
    "apps.track_processing",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "theme/templates",
            BASE_DIR / "theme/templates/apps",
        ],
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRESQL_NAME"),
        "USER": os.getenv("POSTGRESQL_USER"),
        "PASSWORD": os.getenv("POSTGRESQL_PASSWORD"),
        "HOST": os.getenv("POSTGRESQL_HOST"),
        "PORT": os.getenv("POSTGRESQL_PORT"),
    }
}


MINIO_STORAGE_ENDPOINT = os.getenv("MINIO_STORAGE_ENDPOINT")
MINIO_STORAGE_ACCESS_KEY = os.getenv("MINIO_STORAGE_ACCESS_KEY")
MINIO_STORAGE_SECRET_KEY = os.getenv("MINIO_STORAGE_SECRET_KEY")
MINIO_STORAGE_MEDIA_BUCKET_NAME = os.getenv("MINIO_STORAGE_MEDIA_BUCKET_NAME")
MINIO_STORAGE_STATIC_BUCKET_NAME = os.getenv("MINIO_STORAGE_STATIC_BUCKET_NAME")
MINIO_STORAGE_MEDIA_USE_PRESIGNED = os.getenv("MINIO_STORAGE_MEDIA_USE_PRESIGNED")


FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5 МБ
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 МБ


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/"


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
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

TAILWIND_APP_NAME = "apps.theme"
TAILWIND_CONTENT_PATHS = [
    str(BASE_DIR / "theme/templates/**/*.html"),
    str(BASE_DIR / "apps" / "**" / "templates" / "**" / "*.html"),
    str(BASE_DIR / "apps" / "**" / "*.py"),
]
INTERNAL_IPS = ["127.0.0.1"]


# Celery Configuration
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
