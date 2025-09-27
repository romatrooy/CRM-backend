"""
Модель файла/вложения
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class File(Base):
    """Модель файла/вложения"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=True)
    
    # Метаданные файла
    file_size = Column(BigInteger, nullable=False)  # в байтах
    mime_type = Column(String(100), nullable=False)
    file_extension = Column(String(10), nullable=True)
    
    # Описание и теги
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    
    # Связи
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Статус и безопасность
    is_public = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    access_level = Column(String(50), default="private")  # private, team, public
    
    # JSON поля для дополнительных данных
    custom_fields = Column(JSON, default=dict)
    file_metadata = Column(JSON, default=dict)  # exif, dimensions, etc.
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Мягкое удаление
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    contact = relationship("Contact")
    company = relationship("Company")
    deal = relationship("Deal")
    activity = relationship("Activity")
    owner = relationship("User")
