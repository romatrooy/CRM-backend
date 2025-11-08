"""
Модель сделки
"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Numeric, Enum, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timezone
from app.core.database import Base


class DealStatus(str, enum.Enum):
    """Статусы сделки"""
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    COMPLETED = "Завершена"
    CANCELLED = "Отменена"


class Deal(Base):
    """Модель сделки"""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Финансовая информация
    amount = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="RUB")
    probability = Column(Integer, default=0)  # 0-100%
    
    # Статус
    status = Column(Enum(DealStatus), default=DealStatus.NEW, nullable=False, index=True)
    
    # Даты
    expected_close_date = Column(DateTime, nullable=True)
    actual_close_date = Column(DateTime, nullable=True)
    
    # Связи
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)  # Клиент
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Менеджер
    
    # Дополнительная информация
    source = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # JSON поля для дополнительных данных
    custom_fields = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Мягкое удаление
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    contact = relationship("Contact", back_populates="deals")
    company = relationship("Company", back_populates="deals")
    owner = relationship("User")
    activities = relationship("Activity", back_populates="deal")


@event.listens_for(Deal, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    """Автоматическое обновление updated_at при любом изменении сделки"""
    target.updated_at = datetime.now(timezone.utc)
