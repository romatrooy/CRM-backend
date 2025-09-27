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
        stage: Optional[str] = None,
        status: Optional[str] = None,
        contact_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Tuple[List[Deal], int]:
        """Получение списка сделок с фильтрацией"""
        query = select(Deal).where(
            and_(
                Deal.owner_id == owner_id,
                Deal.is_deleted == False
            )
        )
        
        # Поиск
        if search:
            search_filter = or_(
                Deal.title.ilike(f"%{search}%"),
                Deal.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Фильтр по этапу
        if stage:
            query = query.where(Deal.stage == stage)
        
        # Фильтр по статусу
        if status:
            query = query.where(Deal.status == status)
        
        # Фильтр по контакту
        if contact_id:
            query = query.where(Deal.contact_id == contact_id)
        
        # Фильтр по компании
        if company_id:
            query = query.where(Deal.company_id == company_id)
        
        # Получение общего количества
        count_query = select(func.count(Deal.id)).where(
            and_(
                Deal.owner_id == owner_id,
                Deal.is_deleted == False
            )
        )
        
        if search:
            count_query = count_query.where(search_filter)
        if stage:
            count_query = count_query.where(Deal.stage == stage)
        if status:
            count_query = count_query.where(Deal.status == status)
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
                selectinload(Deal.company)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Deal.created_at.desc())
        )
        
        deals = result.scalars().all()
        return deals, total
    
    async def create_deal(self, deal_data: DealCreate, owner_id: int) -> Deal:
        """Создание новой сделки"""
        deal = Deal(
            **deal_data.dict(),
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
