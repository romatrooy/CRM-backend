"""
Модель пользователя
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """Модель пользователя системы"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Дополнительные поля
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="ru")
    
    # JSON поля для дополнительных данных
    preferences = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Мягкое удаление
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
