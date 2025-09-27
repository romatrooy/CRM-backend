"""
Сервис для работы с активностями
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityUpdate


class ActivityService:
    """Сервис для работы с активностями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_activity(self, activity_id: int, owner_id: int) -> Optional[Activity]:
        """Получение активности по ID"""
        result = await self.db.execute(
            select(Activity)
            .where(
                and_(
                    Activity.id == activity_id,
                    Activity.owner_id == owner_id,
                    Activity.is_deleted == False
                )
            )
            .options(
                selectinload(Activity.contact),
                selectinload(Activity.company),
                selectinload(Activity.deal)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_activities(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
        contact_id: Optional[int] = None,
        company_id: Optional[int] = None,
        deal_id: Optional[int] = None
    ) -> Tuple[List[Activity], int]:
        """Получение списка активностей с фильтрацией"""
        query = select(Activity).where(
            and_(
                Activity.owner_id == owner_id,
                Activity.is_deleted == False
            )
        )
        
        # Поиск
        if search:
            search_filter = or_(
                Activity.title.ilike(f"%{search}%"),
                Activity.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Фильтр по типу
        if type:
            query = query.where(Activity.type == type)
        
        # Фильтр по статусу
        if status:
            query = query.where(Activity.status == status)
        
        # Фильтр по контакту
        if contact_id:
            query = query.where(Activity.contact_id == contact_id)
        
        # Фильтр по компании
        if company_id:
            query = query.where(Activity.company_id == company_id)
        
        # Фильтр по сделке
        if deal_id:
            query = query.where(Activity.deal_id == deal_id)
        
        # Получение общего количества
        count_query = select(func.count(Activity.id)).where(
            and_(
                Activity.owner_id == owner_id,
                Activity.is_deleted == False
            )
        )
        
        if search:
            count_query = count_query.where(search_filter)
        if type:
            count_query = count_query.where(Activity.type == type)
        if status:
            count_query = count_query.where(Activity.status == status)
        if contact_id:
            count_query = count_query.where(Activity.contact_id == contact_id)
        if company_id:
            count_query = count_query.where(Activity.company_id == company_id)
        if deal_id:
            count_query = count_query.where(Activity.deal_id == deal_id)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Получение данных
        result = await self.db.execute(
            query.options(
                selectinload(Activity.contact),
                selectinload(Activity.company),
                selectinload(Activity.deal)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Activity.created_at.desc())
        )
        
        activities = result.scalars().all()
        return activities, total
    
    async def create_activity(self, activity_data: ActivityCreate, owner_id: int) -> Activity:
        """Создание новой активности"""
        activity = Activity(
            **activity_data.dict(),
            owner_id=owner_id
        )
        
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity
    
    async def update_activity(
        self,
        activity_id: int,
        activity_update: ActivityUpdate,
        owner_id: int
    ) -> Optional[Activity]:
        """Обновление активности"""
        activity = await self.get_activity(activity_id, owner_id)
        if not activity:
            return None
        
        update_data = activity_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(activity, field, value)
        
        await self.db.commit()
        await self.db.refresh(activity)
        return activity
    
    async def delete_activity(self, activity_id: int, owner_id: int) -> bool:
        """Мягкое удаление активности"""
        activity = await self.get_activity(activity_id, owner_id)
        if not activity:
            return False
        
        activity.is_deleted = True
        await self.db.commit()
        return True
