"""
Сервис для работы с пользователями
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        result = await self.db.execute(
            select(User).where(and_(User.id == user_id, User.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        result = await self.db.execute(
            select(User).where(and_(User.email == email, User.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по имени пользователя"""
        result = await self.db.execute(
            select(User).where(and_(User.username == username, User.is_deleted == False))
        )
        return result.scalar_one_or_none()
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей"""
        result = await self.db.execute(
            select(User)
            .where(User.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        hashed_password = get_password_hash(user_data.password)
        
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            phone=user_data.phone,
            timezone=user_data.timezone,
            language=user_data.language,
            hashed_password=hashed_password
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Обновление пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Мягкое удаление пользователя"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_deleted = True
        await self.db.commit()
        return True
