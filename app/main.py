"""
Основной файл приложения CRM системы
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1.api import api_router

# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="CRM система для управления клиентами, сделками и взаимодействиями",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)

# Подключение роутеров
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    logger.info("Запуск CRM приложения")
    await create_tables()
    logger.info("База данных инициализирована")


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении приложения"""
    logger.info("Завершение работы CRM приложения")


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "CRM Backend API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


@app.get("/health")
async def health_check():
    """Проверка состояния приложения"""
    return {"status": "healthy", "version": settings.APP_VERSION}
