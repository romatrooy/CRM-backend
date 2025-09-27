"""
Схемы для компаний
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, validator


class CompanyBase(BaseModel):
    """Базовая схема компании"""
    name: str
    legal_name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    status: str = "prospect"
    type: Optional[str] = None
    priority: str = "medium"
    parent_company_id: Optional[int] = None
    custom_fields: Dict[str, Any] = {}
    tags: List[str] = []
    social_links: Dict[str, str] = {}


class CompanyCreate(CompanyBase):
    """Схема для создания компании"""
    pass


class CompanyUpdate(BaseModel):
    """Схема для обновления компании"""
    name: Optional[str] = None
    legal_name: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    parent_company_id: Optional[int] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    social_links: Optional[Dict[str, str]] = None


class CompanyInDB(CompanyBase):
    """Схема компании в базе данных"""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_contacted: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Company(CompanyInDB):
    """Публичная схема компании"""
    pass


class CompanyList(BaseModel):
    """Схема списка компаний"""
    items: List[Company]
    total: int
    page: int
    size: int
    pages: int
