"""
Эндпоинты для компаний
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import verify_token
from app.schemas.company import Company, CompanyCreate, CompanyUpdate, CompanyList
from app.schemas.user import User
from app.services.company_service import CompanyService

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


@router.get("/", response_model=CompanyList)
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None, description="Поиск по названию или email"),
    status: str = Query(None, description="Фильтр по статусу"),
    industry: str = Query(None, description="Фильтр по отрасли"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение списка компаний"""
    company_service = CompanyService(db)
    companies, total = await company_service.get_companies(
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        status=status,
        industry=industry
    )
    
    return CompanyList(
        items=companies,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{company_id}", response_model=Company)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение компании по ID"""
    company_service = CompanyService(db)
    company = await company_service.get_company(company_id, current_user.id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Компания не найдена"
        )
    return company


@router.post("/", response_model=Company, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Создание новой компании"""
    company_service = CompanyService(db)
    company = await company_service.create_company(company_data, current_user.id)
    return company


@router.put("/{company_id}", response_model=Company)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Обновление компании"""
    company_service = CompanyService(db)
    company = await company_service.update_company(company_id, company_update, current_user.id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Компания не найдена"
        )
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Удаление компании"""
    company_service = CompanyService(db)
    success = await company_service.delete_company(company_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Компания не найдена"
        )
