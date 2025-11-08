"""
Эндпоинты для файлов
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.security import verify_token
from app.schemas.file import File, FileCreate, FileList
from app.schemas.user import User
from app.services.file_service import FileService

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


@router.get("/", response_model=FileList)
async def get_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str = Query(None, description="Поиск по названию файла"),
    mime_type: str = Query(None, description="Фильтр по типу файла"),
    contact_id: int = Query(None, description="Фильтр по контакту"),
    company_id: int = Query(None, description="Фильтр по компании"),
    deal_id: int = Query(None, description="Фильтр по сделке"),
    activity_id: int = Query(None, description="Фильтр по активности"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение списка файлов"""
    file_service = FileService(db)
    files, total = await file_service.get_files(
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        mime_type=mime_type,
        contact_id=contact_id,
        company_id=company_id,
        deal_id=deal_id,
        activity_id=activity_id
    )
    
    return FileList(
        items=files,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{file_id}", response_model=File)
async def get_file(
    file_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Получение файла по ID"""
    file_service = FileService(db)
    file = await file_service.get_file(file_id, current_user.id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден"
        )
    return file


@router.post("/upload", response_model=File, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    title: str = Query(None, description="Название файла"),
    description: str = Query(None, description="Описание файла"),
    contact_id: int = Query(None, description="ID контакта"),
    company_id: int = Query(None, description="ID компании"),
    deal_id: int = Query(None, description="ID сделки"),
    activity_id: int = Query(None, description="ID активности"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Загрузка файла"""
    file_service = FileService(db)
    
    # Создаем данные для файла
    file_data = FileCreate(
        filename=file.filename,
        title=title,
        description=description,
        contact_id=contact_id,
        company_id=company_id,
        deal_id=deal_id,
        activity_id=activity_id
    )
    
    uploaded_file = await file_service.upload_file(file, file_data, current_user.id)
    return uploaded_file


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Удаление файла"""
    file_service = FileService(db)
    success = await file_service.delete_file(file_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден"
        )
