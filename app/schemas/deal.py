"""
Схемы для сделок
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, validator


class DealBase(BaseModel):
    """Базовая схема сделки"""
    title: str
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: str = "RUB"
    probability: int = 0
    stage: str
    status: str = "open"
    expected_close_date: Optional[datetime] = None
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Dict[str, Any] = {}
    tags: List[str] = []
    
    @validator('probability')
    def validate_probability(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Вероятность должна быть от 0 до 100')
        return v


class DealCreate(DealBase):
    """Схема для создания сделки"""
    pass


class DealUpdate(BaseModel):
    """Схема для обновления сделки"""
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    probability: Optional[int] = None
    stage: Optional[str] = None
    status: Optional[str] = None
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class DealInDB(DealBase):
    """Схема сделки в базе данных"""
    id: int
    owner_id: int
    actual_close_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Deal(DealInDB):
    """Публичная схема сделки"""
    pass


class DealList(BaseModel):
    """Схема списка сделок"""
    items: List[Deal]
    total: int
    page: int
    size: int
    pages: int
