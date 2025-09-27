"""
Сервис для работы с компаниями
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Сервис для работы с компаниями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_company(self, company_id: int, owner_id: int) -> Optional[Company]:
        """Получение компании по ID"""
        result = await self.db.execute(
            select(Company)
            .where(
                and_(
                    Company.id == company_id,
                    Company.owner_id == owner_id,
                    Company.is_deleted == False
                )
            )
            .options(selectinload(Company.parent_company))
        )
        return result.scalar_one_or_none()
    
    async def get_companies(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        industry: Optional[str] = None
    ) -> Tuple[List[Company], int]:
        """Получение списка компаний с фильтрацией"""
        query = select(Company).where(
            and_(
                Company.owner_id == owner_id,
                Company.is_deleted == False
            )
        )
        
        # Поиск
        if search:
            search_filter = or_(
                Company.name.ilike(f"%{search}%"),
                Company.email.ilike(f"%{search}%"),
                Company.website.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Фильтр по статусу
        if status:
            query = query.where(Company.status == status)
        
        # Фильтр по отрасли
        if industry:
            query = query.where(Company.industry == industry)
        
        # Получение общего количества
        count_query = select(func.count(Company.id)).where(
            and_(
                Company.owner_id == owner_id,
                Company.is_deleted == False
            )
        )
        
        if search:
            count_query = count_query.where(search_filter)
        if status:
            count_query = count_query.where(Company.status == status)
        if industry:
            count_query = count_query.where(Company.industry == industry)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Получение данных
        result = await self.db.execute(
            query.options(selectinload(Company.parent_company))
            .offset(skip)
            .limit(limit)
            .order_by(Company.created_at.desc())
        )
        
        companies = result.scalars().all()
        return companies, total
    
    async def create_company(self, company_data: CompanyCreate, owner_id: int) -> Company:
        """Создание новой компании"""
        company = Company(
            **company_data.dict(),
            owner_id=owner_id
        )
        
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def update_company(
        self,
        company_id: int,
        company_update: CompanyUpdate,
        owner_id: int
    ) -> Optional[Company]:
        """Обновление компании"""
        company = await self.get_company(company_id, owner_id)
        if not company:
            return None
        
        update_data = company_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)
        
        await self.db.commit()
        await self.db.refresh(company)
        return company
    
    async def delete_company(self, company_id: int, owner_id: int) -> bool:
        """Мягкое удаление компании"""
        company = await self.get_company(company_id, owner_id)
        if not company:
            return False
        
        company.is_deleted = True
        await self.db.commit()
        return True
