import os

from celery import Celery

# Важно: Установите DJANGO_SETTINGS_MODULE перед созданием Celery приложения
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("music_stream")

# Загружаем настройки из settings.py с префиксом CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач во всех приложениях Django
app.autodiscover_tasks()


# Для отладки
@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return "Broker URL: " + app.conf.broker_url
