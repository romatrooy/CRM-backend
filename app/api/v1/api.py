"""
Основной роутер API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, contacts, companies, deals, activities, files

api_router = APIRouter()

# Подключение всех роутеров
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(deals.router, prefix="/deals", tags=["deals"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
