"""
Задачи для отправки email
"""
from typing import List
from app.core.celery import celery_app


@celery_app.task
def send_welcome_email(user_email: str, user_name: str):
    """Отправка приветственного email новому пользователю"""
    # Здесь должна быть логика отправки email
    print(f"Отправка приветственного email пользователю {user_name} ({user_email})")
    return f"Welcome email sent to {user_email}"


@celery_app.task
def send_password_reset_email(user_email: str, reset_token: str):
    """Отправка email для сброса пароля"""
    # Здесь должна быть логика отправки email
    print(f"Отправка email для сброса пароля пользователю {user_email}")
    return f"Password reset email sent to {user_email}"


@celery_app.task
def send_notification_email(user_email: str, subject: str, message: str):
    """Отправка уведомительного email"""
    # Здесь должна быть логика отправки email
    print(f"Отправка уведомления пользователю {user_email}: {subject}")
    return f"Notification email sent to {user_email}"
