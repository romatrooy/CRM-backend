"""
Задачи для уведомлений
"""
from typing import List, Dict, Any
from app.core.celery import celery_app


@celery_app.task
def send_reminders():
    """Отправка напоминаний о предстоящих активностях"""
    # Здесь должна быть логика отправки напоминаний
    print("Отправка напоминаний о предстоящих активностях")
    return "Reminders sent"


@celery_app.task
def send_deal_reminder(deal_id: int, user_id: int):
    """Отправка напоминания о сделке"""
    # Здесь должна быть логика отправки напоминания о сделке
    print(f"Отправка напоминания о сделке {deal_id} пользователю {user_id}")
    return f"Deal reminder sent for deal {deal_id}"


@celery_app.task
def send_activity_reminder(activity_id: int, user_id: int):
    """Отправка напоминания об активности"""
    # Здесь должна быть логика отправки напоминания об активности
    print(f"Отправка напоминания об активности {activity_id} пользователю {user_id}")
    return f"Activity reminder sent for activity {activity_id}"


@celery_app.task
def send_birthday_notifications():
    """Отправка уведомлений о днях рождения"""
    # Здесь должна быть логика отправки уведомлений о днях рождения
    print("Отправка уведомлений о днях рождения")
    return "Birthday notifications sent"
