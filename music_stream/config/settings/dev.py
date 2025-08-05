from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]


STORAGES = {
    "default": {
        "BACKEND": "minio_storage.MinioMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_SECURE = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Настройки для отладки
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

# Настройки электронной почты
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Статика в режиме разработки
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# MinIO для разработки
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "qimpe"
MINIO_SECRET_KEY = "pass12345"


# * Для tailwind
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"


CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
