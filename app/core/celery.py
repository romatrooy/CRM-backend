"""
Настройка Celery для фоновых задач
"""
from celery import Celery
from app.core.config import settings

# Создание экземпляра Celery
celery_app = Celery(
    "crm",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email",
        "app.tasks.import_export",
        "app.tasks.reports",
        "app.tasks.notifications"
    ]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Периодические задачи
celery_app.conf.beat_schedule = {
    "cleanup-expired-tokens": {
        "task": "app.tasks.cleanup.cleanup_expired_tokens",
        "schedule": 3600.0,  # Каждый час
    },
    "send-reminders": {
        "task": "app.tasks.notifications.send_reminders",
        "schedule": 300.0,  # Каждые 5 минут
    },
    "generate-daily-reports": {
        "task": "app.tasks.reports.generate_daily_reports",
        "schedule": 86400.0,  # Каждый день
    },
}
