"""
Модель активности/взаимодействия
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Activity(Base):
    """Модель активности/взаимодействия с клиентом"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # call, email, meeting, task, note, etc.
    
    # Статус и приоритет
    status = Column(String(50), default="pending")  # pending, completed, cancelled
    priority = Column(String(20), default="medium")  # low, medium, high
    
    # Даты
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    # Связи
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Дополнительная информация
    location = Column(String(255), nullable=True)
    duration = Column(Integer, nullable=True)  # в минутах
    outcome = Column(Text, nullable=True)
    
    # JSON поля для дополнительных данных
    custom_fields = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Мягкое удаление
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    contact = relationship("Contact", back_populates="activities")
    company = relationship("Company", back_populates="activities")
    deal = relationship("Deal", back_populates="activities")
    owner = relationship("User", foreign_keys=[owner_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
