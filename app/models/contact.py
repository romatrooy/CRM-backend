"""
Модель контакта
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Contact(Base):
    """Модель контакта/лида"""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True, index=True)
    
    # Дополнительная информация
    job_title = Column(String(200), nullable=True)
    department = Column(String(200), nullable=True)
    birthday = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Статус и тип
    status = Column(String(50), default="lead")  # lead, prospect, customer, partner
    source = Column(String(100), nullable=True)  # website, referral, cold_call, etc.
    priority = Column(String(20), default="medium")  # low, medium, high
    
    # Связи
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # JSON поля для дополнительных данных
    custom_fields = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_contacted = Column(DateTime(timezone=True), nullable=True)
    
    # Мягкое удаление
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    company = relationship("Company", back_populates="contacts")
    owner = relationship("User")
    activities = relationship("Activity", back_populates="contact")
    deals = relationship("Deal", back_populates="contact")
