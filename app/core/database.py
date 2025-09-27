"""
Настройка базы данных
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Синхронный движок для миграций
engine = create_engine(settings.DATABASE_URL)

# Асинхронный движок для приложения
async_engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=settings.DEBUG,
    future=True
)

# Сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый класс для моделей
Base = declarative_base()


async def get_async_session():
    """Получение асинхронной сессии базы данных"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Создание таблиц в базе данных"""
    async with async_engine.begin() as conn:
        # Импортируем все модели для создания таблиц
        from app.models import user, contact, company, deal, activity, file
        await conn.run_sync(Base.metadata.create_all)
