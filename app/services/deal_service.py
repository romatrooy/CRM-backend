"""
Сервис для работы со сделками
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.deal import Deal
from app.schemas.deal import DealCreate, DealUpdate


class DealService:
    """Сервис для работы со сделками"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_deal(self, deal_id: int, owner_id: int) -> Optional[Deal]:
        """Получение сделки по ID"""
        result = await self.db.execute(
            select(Deal)
            .where(
                and_(
                    Deal.id == deal_id,
                    Deal.owner_id == owner_id,
                    Deal.is_deleted == False
                )
            )
            .options(
                selectinload(Deal.contact),
                selectinload(Deal.company)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_deals(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        manager_id: Optional[int] = None,  # Фильтр по менеджеру
        contact_id: Optional[int] = None,  # Фильтр по клиенту
        company_id: Optional[int] = None
    ) -> Tuple[List[Deal], int]:
        """Получение списка сделок с фильтрацией"""
        # Базовый фильтр: по умолчанию показываем сделки текущего пользователя
        # Если указан manager_id, фильтруем по нему
        manager_filter = Deal.owner_id == (manager_id if manager_id else owner_id)
        
        query = select(Deal).where(
            and_(
                manager_filter,
                Deal.is_deleted == False
            )
        )
        
        # Поиск
        search_filter = None
        if search:
            search_filter = or_(
                Deal.title.ilike(f"%{search}%"),
                Deal.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Фильтр по статусу
        if status:
            from app.models.deal import DealStatus
            try:
                status_enum = DealStatus(status)
                query = query.where(Deal.status == status_enum)
            except ValueError:
                # Если статус невалидный, просто игнорируем фильтр
                pass
        
        # Фильтр по клиенту (contact_id)
        if contact_id:
            query = query.where(Deal.contact_id == contact_id)
        
        # Фильтр по компании
        if company_id:
            query = query.where(Deal.company_id == company_id)
        
        # Получение общего количества
        count_query = select(func.count(Deal.id)).where(
            and_(
                manager_filter,
                Deal.is_deleted == False
            )
        )
        
        if search_filter:
            count_query = count_query.where(search_filter)
        if status:
            from app.models.deal import DealStatus
            try:
                status_enum = DealStatus(status)
                count_query = count_query.where(Deal.status == status_enum)
            except ValueError:
                pass
        if contact_id:
            count_query = count_query.where(Deal.contact_id == contact_id)
        if company_id:
            count_query = count_query.where(Deal.company_id == company_id)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Получение данных
        result = await self.db.execute(
            query.options(
                selectinload(Deal.contact),
                selectinload(Deal.company),
                selectinload(Deal.owner)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Deal.created_at.desc())
        )
        
        deals = result.scalars().all()
        return deals, total
    
    async def create_deal(self, deal_data: DealCreate, owner_id: int) -> Deal:
        """Создание новой сделки"""
        deal_dict = deal_data.dict()
        # Убеждаемся, что contact_id и company_id равны None, если они 0 или None
        if deal_dict.get('contact_id') == 0:
            deal_dict['contact_id'] = None
        if deal_dict.get('company_id') == 0:
            deal_dict['company_id'] = None
        
        deal = Deal(
            **deal_dict,
            owner_id=owner_id
        )
        
        self.db.add(deal)
        await self.db.commit()
        await self.db.refresh(deal)
        return deal
    
    async def update_deal(
        self,
        deal_id: int,
        deal_update: DealUpdate,
        owner_id: int
    ) -> Optional[Deal]:
        """Обновление сделки"""
        deal = await self.get_deal(deal_id, owner_id)
        if not deal:
            return None
        
        update_data = deal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(deal, field, value)
        
        # updated_at обновится автоматически через event listener
        await self.db.commit()
        await self.db.refresh(deal)
        return deal
    
    async def update_deal_status(
        self,
        deal_id: int,
        status,
        owner_id: int
    ) -> Optional[Deal]:
        """Обновление статуса сделки"""
        deal = await self.get_deal(deal_id, owner_id)
        if not deal:
            return None
        
        deal.status = status
        # updated_at обновится автоматически через event listener
        
        await self.db.commit()
        await self.db.refresh(deal)
        return deal
    
    async def delete_deal(self, deal_id: int, owner_id: int) -> bool:
        """Мягкое удаление сделки"""
        deal = await self.get_deal(deal_id, owner_id)
        if not deal:
            return False
        
        deal.is_deleted = True
        await self.db.commit()
        return True
