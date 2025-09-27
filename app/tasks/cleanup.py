"""
Задачи для очистки данных
"""
from app.core.celery import celery_app


@celery_app.task
def cleanup_expired_tokens():
    """Очистка истекших токенов"""
    # Здесь должна быть логика очистки истекших токенов
    print("Очистка истекших токенов")
    return "Expired tokens cleaned up"


@celery_app.task
def cleanup_old_files():
    """Очистка старых файлов"""
    # Здесь должна быть логика очистки старых файлов
    print("Очистка старых файлов")
    return "Old files cleaned up"


@celery_app.task
def cleanup_soft_deleted_records():
    """Окончательное удаление мягко удаленных записей"""
    # Здесь должна быть логика окончательного удаления мягко удаленных записей
    print("Окончательное удаление мягко удаленных записей")
    return "Soft deleted records permanently removed"
