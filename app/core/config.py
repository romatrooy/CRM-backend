"""
Конфигурация приложения
"""
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    APP_NAME: str = "CRM Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # API настройки
    API_V1_STR: str = "/api/v1"
    
    # База данных
    DATABASE_URL: str
    DATABASE_URL_ASYNC: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # JWT настройки
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Файловое хранилище
    STORAGE_TYPE: str = "local"  # local, s3, minio
    S3_BUCKET_NAME: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None
    
    # Email настройки
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Создание экземпляра настроек
settings = Settings()
