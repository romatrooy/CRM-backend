"""
Сервис для работы с контактами
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactService:
    """Сервис для работы с контактами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_contact(self, contact_id: int, owner_id: int) -> Optional[Contact]:
        """Получение контакта по ID"""
        result = await self.db.execute(
            select(Contact)
            .where(
                and_(
                    Contact.id == contact_id,
                    Contact.owner_id == owner_id,
                    Contact.is_deleted == False
                )
            )
            .options(selectinload(Contact.company))
        )
        return result.scalar_one_or_none()
    
    async def get_contacts(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        company_id: Optional[int] = None
    ) -> Tuple[List[Contact], int]:
        """Получение списка контактов с фильтрацией"""
        query = select(Contact).where(
            and_(
                Contact.owner_id == owner_id,
                Contact.is_deleted == False
            )
        )
        
        # Поиск
        if search:
            search_filter = or_(
                Contact.first_name.ilike(f"%{search}%"),
                Contact.last_name.ilike(f"%{search}%"),
                Contact.email.ilike(f"%{search}%"),
                Contact.phone.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Фильтр по статусу
        if status:
            query = query.where(Contact.status == status)
        
        # Фильтр по компании
        if company_id:
            query = query.where(Contact.company_id == company_id)
        
        # Получение общего количества
        count_query = select(func.count(Contact.id)).where(
            and_(
                Contact.owner_id == owner_id,
                Contact.is_deleted == False
            )
        )
        
        if search:
            count_query = count_query.where(search_filter)
        if status:
            count_query = count_query.where(Contact.status == status)
        if company_id:
            count_query = count_query.where(Contact.company_id == company_id)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Получение данных
        result = await self.db.execute(
            query.options(selectinload(Contact.company))
            .offset(skip)
            .limit(limit)
            .order_by(Contact.created_at.desc())
        )
        
        contacts = result.scalars().all()
        return contacts, total
    
    async def create_contact(self, contact_data: ContactCreate, owner_id: int) -> Contact:
        """Создание нового контакта"""
        contact = Contact(
            **contact_data.dict(),
            owner_id=owner_id
        )
        
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact
    
    async def update_contact(
        self,
        contact_id: int,
        contact_update: ContactUpdate,
        owner_id: int
    ) -> Optional[Contact]:
        """Обновление контакта"""
        contact = await self.get_contact(contact_id, owner_id)
        if not contact:
            return None
        
        update_data = contact_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)
        
        await self.db.commit()
        await self.db.refresh(contact)
        return contact
    
    async def delete_contact(self, contact_id: int, owner_id: int) -> bool:
        """Мягкое удаление контакта"""
        contact = await self.get_contact(contact_id, owner_id)
        if not contact:
            return False
        
        contact.is_deleted = True
        await self.db.commit()
        return True
