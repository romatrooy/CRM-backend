"""
Эндпоинты для контактов
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import verify_token
from app.schemas.contact import Contact, ContactCreate, ContactUpdate, ContactList
from app.schemas.user import User
from app.services.contact_service import ContactService

router = APIRouter()


async def get_current_user(
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """Получение текущего пользователя"""
    from app.services.user_service import UserService
    user_service = UserService(db)
    user = await user_service.get_by_id(token["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.get("/", response_model=ContactList)
async def get_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None, description="Поиск по имени, email или телефону"),
    status: str = Query(None, description="Фильтр по статусу"),
    company_id: int = Query(None, description="Фильтр по компании"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение списка контактов"""
    contact_service = ContactService(db)
    contacts, total = await contact_service.get_contacts(
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        status=status,
        company_id=company_id
    )
    
    return ContactList(
        items=contacts,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение контакта по ID"""
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, current_user.id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )
    return contact


@router.post("/", response_model=Contact, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Создание нового контакта"""
    contact_service = ContactService(db)
    contact = await contact_service.create_contact(contact_data, current_user.id)
    return contact


@router.put("/{contact_id}", response_model=Contact)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Обновление контакта"""
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, contact_update, current_user.id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Удаление контакта"""
    contact_service = ContactService(db)
    success = await contact_service.delete_contact(contact_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )
