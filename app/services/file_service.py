"""
Сервис для работы с файлами
"""
from typing import List, Optional, Tuple
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.file import File
from app.schemas.file import FileCreate


class FileService:
    """Сервис для работы с файлами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_file(self, file_id: int, owner_id: int) -> Optional[File]:
        """Получение файла по ID"""
        result = await self.db.execute(
            select(File)
            .where(
                and_(
                    File.id == file_id,
                    File.owner_id == owner_id,
                    File.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_files(
        self,
        owner_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        mime_type: Optional[str] = None,
        contact_id: Optional[int] = None,
        company_id: Optional[int] = None,
        deal_id: Optional[int] = None,
        activity_id: Optional[int] = None
    ) -> Tuple[List[File], int]:
        """Получение списка файлов с фильтрацией"""
        query = select(File).where(
            and_(
                File.owner_id == owner_id,
                File.is_deleted == False
            )
        )
        
        # Поиск
        if search:
            search_filter = or_(
                File.filename.ilike(f"%{search}%"),
                File.original_filename.ilike(f"%{search}%"),
                File.title.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Фильтр по типу файла
        if mime_type:
            query = query.where(File.mime_type == mime_type)
        
        # Фильтр по контакту
        if contact_id:
            query = query.where(File.contact_id == contact_id)
        
        # Фильтр по компании
        if company_id:
            query = query.where(File.company_id == company_id)
        
        # Фильтр по сделке
        if deal_id:
            query = query.where(File.deal_id == deal_id)
        
        # Фильтр по активности
        if activity_id:
            query = query.where(File.activity_id == activity_id)
        
        # Получение общего количества
        count_query = select(func.count(File.id)).where(
            and_(
                File.owner_id == owner_id,
                File.is_deleted == False
            )
        )
        
        if search:
            count_query = count_query.where(search_filter)
        if mime_type:
            count_query = count_query.where(File.mime_type == mime_type)
        if contact_id:
            count_query = count_query.where(File.contact_id == contact_id)
        if company_id:
            count_query = count_query.where(File.company_id == company_id)
        if deal_id:
            count_query = count_query.where(File.deal_id == deal_id)
        if activity_id:
            count_query = count_query.where(File.activity_id == activity_id)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Получение данных
        result = await self.db.execute(
            query.offset(skip)
            .limit(limit)
            .order_by(File.created_at.desc())
        )
        
        files = result.scalars().all()
        return files, total
    
    async def upload_file(self, file: UploadFile, file_data: FileCreate, owner_id: int) -> File:
        """Загрузка файла"""
        # Здесь должна быть логика сохранения файла в файловую систему или S3
        # Пока создаем запись в базе данных
        
        file_record = File(
            filename=file.filename,
            original_filename=file.filename,
            file_path=f"/uploads/{file.filename}",  # Временный путь
            file_size=file.size or 0,
            mime_type=file.content_type or "application/octet-stream",
            file_extension=file.filename.split('.')[-1] if '.' in file.filename else None,
            title=file_data.title,
            description=file_data.description,
            contact_id=file_data.contact_id,
            company_id=file_data.company_id,
            deal_id=file_data.deal_id,
            activity_id=file_data.activity_id,
            owner_id=owner_id
        )
        
        self.db.add(file_record)
        await self.db.commit()
        await self.db.refresh(file_record)
        return file_record
    
    async def delete_file(self, file_id: int, owner_id: int) -> bool:
        """Мягкое удаление файла"""
        file = await self.get_file(file_id, owner_id)
        if not file:
            return False
        
        file.is_deleted = True
        await self.db.commit()
        return True
