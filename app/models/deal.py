"""
Модель сделки
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Deal(Base):
    """Модель сделки/опortunity"""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Финансовая информация
    amount = Column(Numeric(15, 2), nullable=True)
    currency = Column(String(3), default="RUB")
    probability = Column(Integer, default=0)  # 0-100%
    
    # Статус и этапы
    stage = Column(String(100), nullable=False)  # qualification, proposal, negotiation, closed_won, closed_lost
    status = Column(String(50), default="open")  # open, won, lost, cancelled
    
    # Даты
    expected_close_date = Column(DateTime, nullable=True)
    actual_close_date = Column(DateTime, nullable=True)
    
    # Связи
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Дополнительная информация
    source = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
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
    contact = relationship("Contact", back_populates="deals")
    company = relationship("Company", back_populates="deals")
    owner = relationship("User")
    activities = relationship("Activity", back_populates="deal")
