"""
Модель компании
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Company(Base):
    """Модель компании/организации"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(255), nullable=False, index=True)
    legal_name = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)  # startup, small, medium, large, enterprise
    
    # Контактная информация
    website = Column(String(500), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    fax = Column(String(20), nullable=True)
    
    # Адрес
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    
    # Дополнительная информация
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Статус и тип
    status = Column(String(50), default="prospect")  # prospect, customer, partner, competitor
    type = Column(String(50), nullable=True)  # client, vendor, partner, etc.
    priority = Column(String(20), default="medium")  # low, medium, high
    
    # Связи
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # JSON поля для дополнительных данных
    custom_fields = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    social_links = Column(JSON, default=dict)  # linkedin, twitter, facebook, etc.
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_contacted = Column(DateTime(timezone=True), nullable=True)
    
    # Мягкое удаление
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    owner = relationship("User")
    parent_company = relationship("Company", remote_side=[id])
    contacts = relationship("Contact", back_populates="company")
    deals = relationship("Deal", back_populates="company")
    activities = relationship("Activity", back_populates="company")
