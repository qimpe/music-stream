from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored_console": {
            "()": "apps.core.logger.formatters.ColoredFormatter",
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "plain_file": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored_console",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs.log",
            "when": "midnight",
            "backupCount": 7,
            "formatter": "plain_file",  # Без цветов для файла
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.utils.autoreload": {
            "handlers": ["console"],
            "level": "INFO",  # Понижаем уровень для autoreload
            "propagate": False,
        },
        "apps": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "middleware": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",  # Исправлено: ERROR вместо error
    },
}


STORAGES = {
    "default": {
        "BACKEND": "minio_storage.MinioMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


STATIC_URL = "/static/"

# Для разработки: где искать статические файлы
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Основная папка со статикой
    BASE_DIR / "apps/theme/static_src",  # Исходники Tailwind
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


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
#NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"
