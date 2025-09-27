"""
Эндпоинты для сделок
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import verify_token
from app.schemas.deal import Deal, DealCreate, DealUpdate, DealList
from app.schemas.user import User
from app.services.deal_service import DealService

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


@router.get("/", response_model=DealList)
async def get_deals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None, description="Поиск по названию"),
    stage: str = Query(None, description="Фильтр по этапу"),
    status: str = Query(None, description="Фильтр по статусу"),
    contact_id: int = Query(None, description="Фильтр по контакту"),
    company_id: int = Query(None, description="Фильтр по компании"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение списка сделок"""
    deal_service = DealService(db)
    deals, total = await deal_service.get_deals(
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        stage=stage,
        status=status,
        contact_id=contact_id,
        company_id=company_id
    )
    
    return DealList(
        items=deals,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{deal_id}", response_model=Deal)
async def get_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение сделки по ID"""
    deal_service = DealService(db)
    deal = await deal_service.get_deal(deal_id, current_user.id)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сделка не найдена"
        )
    return deal


@router.post("/", response_model=Deal, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Создание новой сделки"""
    deal_service = DealService(db)
    deal = await deal_service.create_deal(deal_data, current_user.id)
    return deal


@router.put("/{deal_id}", response_model=Deal)
async def update_deal(
    deal_id: int,
    deal_update: DealUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Обновление сделки"""
    deal_service = DealService(db)
    deal = await deal_service.update_deal(deal_id, deal_update, current_user.id)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сделка не найдена"
        )
    return deal


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Удаление сделки"""
    deal_service = DealService(db)
    success = await deal_service.delete_deal(deal_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сделка не найдена"
        )
