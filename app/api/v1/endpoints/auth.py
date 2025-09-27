"""
Эндпоинты аутентификации
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.core.security import create_access_token, create_refresh_token, verify_token, get_password_hash, verify_password
from app.schemas.user import User, UserCreate, UserLogin, Token
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Регистрация нового пользователя"""
    user_service = UserService(db)
    
    # Проверяем, существует ли пользователь
    existing_user = await user_service.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    existing_username = await user_service.get_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Создаем пользователя
    user = await user_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Вход в систему"""
    user_service = UserService(db)
    
    # Получаем пользователя по email
    user = await user_service.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт деактивирован"
        )
    
    # Создаем токены
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_session)
) -> Any:
    """Обновление токена доступа"""
    try:
        payload = verify_token(refresh_token, token_type="refresh")
        user_id = int(payload.get("sub"))
        
        user_service = UserService(db)
        user = await user_service.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или неактивен"
            )
        
        # Создаем новые токены
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен"
        )
