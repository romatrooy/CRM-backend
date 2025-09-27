"""
Схемы для активностей
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class ActivityBase(BaseModel):
    """Базовая схема активности"""
    title: str
    description: Optional[str] = None
    type: str
    status: str = "pending"
    priority: str = "medium"
    scheduled_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    deal_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    location: Optional[str] = None
    duration: Optional[int] = None
    outcome: Optional[str] = None
    custom_fields: Dict[str, Any] = {}
    tags: List[str] = []


class ActivityCreate(ActivityBase):
    """Схема для создания активности"""
    pass


class ActivityUpdate(BaseModel):
    """Схема для обновления активности"""
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    deal_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    location: Optional[str] = None
    duration: Optional[int] = None
    outcome: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class ActivityInDB(ActivityBase):
    """Схема активности в базе данных"""
    id: int
    owner_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Activity(ActivityInDB):
    """Публичная схема активности"""
    pass


class ActivityList(BaseModel):
    """Схема списка активностей"""
    items: List[Activity]
    total: int
    page: int
    size: int
    pages: int
