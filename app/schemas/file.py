"""
Схемы для файлов
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class FileBase(BaseModel):
    """Базовая схема файла"""
    filename: str
    title: Optional[str] = None
    description: Optional[str] = None
    contact_id: Optional[int] = None
    company_id: Optional[int] = None
    deal_id: Optional[int] = None
    activity_id: Optional[int] = None
    custom_fields: Dict[str, Any] = {}
    tags: List[str] = []


class FileCreate(FileBase):
    """Схема для создания файла"""
    pass


class FileInDB(FileBase):
    """Схема файла в базе данных"""
    id: int
    original_filename: str
    file_path: str
    file_url: Optional[str] = None
    file_size: int
    mime_type: str
    file_extension: Optional[str] = None
    owner_id: int
    is_public: bool = False
    is_encrypted: bool = False
    access_level: str = "private"
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class File(FileInDB):
    """Публичная схема файла"""
    pass


class FileList(BaseModel):
    """Схема списка файлов"""
    items: List[File]
    total: int
    page: int
    size: int
    pages: int
