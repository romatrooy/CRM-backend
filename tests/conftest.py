"""
Конфигурация для тестов
"""
import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_async_session, Base
from app.core.config import settings

# Тестовая база данных
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Создание тестового движка
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    future=True
)

# Создание тестовой сессии
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Создание тестовой сессии базы данных"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    """Создание тестового клиента"""
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_async_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Создание тестового пользователя"""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_verified=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
