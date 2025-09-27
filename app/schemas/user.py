"""
Схемы для пользователей
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    username: str
    full_name: str
    phone: Optional[str] = None
    timezone: str = "UTC"
    language: str = "ru"


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserInDB(UserBase):
    """Схема пользователя в базе данных"""
    id: int
    is_active: bool
    is_superuser: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """Публичная схема пользователя"""
    pass


class UserLogin(BaseModel):
    """Схема для входа в систему"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Схема токена"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные токена"""
    user_id: Optional[int] = None
    username: Optional[str] = None
