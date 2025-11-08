"""
Эндпоинты для пользователей
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import verify_token
from app.schemas.user import User, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


async def get_current_user(
    token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """Получение текущего пользователя"""
    user_service = UserService(db)
    # В токене используется ключ "sub" для хранения user_id
    user_id = int(token.get("sub"))
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение информации о текущем пользователе"""
    return current_user


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Обновление информации о текущем пользователе"""
    user_service = UserService(db)
    updated_user = await user_service.update_user(current_user.id, user_update)
    return updated_user


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение списка пользователей (только для суперпользователей)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа"
        )
    
    user_service = UserService(db)
    users = await user_service.get_users(skip=skip, limit=limit)
    return users
