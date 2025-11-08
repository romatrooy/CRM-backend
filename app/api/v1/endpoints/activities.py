"""
Эндпоинты для активностей
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import verify_token
from app.schemas.activity import Activity, ActivityCreate, ActivityUpdate, ActivityList
from app.schemas.user import User
from app.services.activity_service import ActivityService

router = APIRouter()


async def get_current_user(
    token: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """Получение текущего пользователя"""
    from app.services.user_service import UserService
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


@router.get("/", response_model=ActivityList)
async def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None, description="Поиск по названию"),
    type: str = Query(None, description="Фильтр по типу"),
    status: str = Query(None, description="Фильтр по статусу"),
    contact_id: int = Query(None, description="Фильтр по контакту"),
    company_id: int = Query(None, description="Фильтр по компании"),
    deal_id: int = Query(None, description="Фильтр по сделке"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение списка активностей"""
    activity_service = ActivityService(db)
    activities, total = await activity_service.get_activities(
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        type=type,
        status=status,
        contact_id=contact_id,
        company_id=company_id,
        deal_id=deal_id
    )
    
    return ActivityList(
        items=activities,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение активности по ID"""
    activity_service = ActivityService(db)
    activity = await activity_service.get_activity(activity_id, current_user.id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активность не найдена"
        )
    return activity


@router.post("/", response_model=Activity, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ActivityCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Создание новой активности"""
    activity_service = ActivityService(db)
    activity = await activity_service.create_activity(activity_data, current_user.id)
    return activity


@router.put("/{activity_id}", response_model=Activity)
async def update_activity(
    activity_id: int,
    activity_update: ActivityUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Обновление активности"""
    activity_service = ActivityService(db)
    activity = await activity_service.update_activity(activity_id, activity_update, current_user.id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активность не найдена"
        )
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Удаление активности"""
    activity_service = ActivityService(db)
    success = await activity_service.delete_activity(activity_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активность не найдена"
        )
