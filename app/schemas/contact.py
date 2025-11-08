"""
Схемы для контактов
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


class ContactBase(BaseModel):
    """Базовая схема контакта"""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    birthday: Optional[datetime] = None
    notes: Optional[str] = None
    status: str = "lead"
    source: Optional[str] = None
    priority: str = "medium"
    company_id: Optional[int] = None
    custom_fields: Dict[str, Any] = {}
    tags: List[str] = []
    
    @validator('company_id')
    def validate_company_id(cls, v):
        """Преобразуем 0 в None для внешнего ключа"""
        return None if v == 0 else v
    
    @validator('birthday')
    def validate_birthday_timezone(cls, v):
        """Преобразуем timezone-aware datetime в timezone-naive для birthday"""
        if v is not None and v.tzinfo is not None:
            # Убираем timezone информацию
            return v.replace(tzinfo=None)
        return v


class ContactCreate(ContactBase):
    """Схема для создания контакта"""
    pass


class ContactUpdate(BaseModel):
    """Схема для обновления контакта"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    birthday: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    priority: Optional[str] = None
    company_id: Optional[int] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class ContactInDB(ContactBase):
    """Схема контакта в базе данных"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Contact(ContactInDB):
    """Публичная схема контакта"""
    pass


class ContactList(BaseModel):
    """Схема списка контактов"""
    items: List[Contact]
    total: int
    page: int
    size: int
    pages: int
