"""
Клиент для работы с CRM API
"""
import httpx
from typing import Optional, Dict, Any, List
from app.bot.config import bot_settings


class APIClient:
    """Клиент для взаимодействия с API"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or bot_settings.API_BASE_URL
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        """Установка JWT токена"""
        self.token = token
    
    def clear_token(self):
        """Очистка токена"""
        self.token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Получение заголовков для запросов"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Авторизация в системе"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                data={
                    "username": username,
                    "password": password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_companies(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение списка компаний"""
        params = {"skip": skip, "limit": limit}
        if search:
            params["search"] = search
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/companies/",
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_company(self, company_id: int) -> Dict[str, Any]:
        """Получение компании по ID"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/companies/{company_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_contacts(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение списка контактов"""
        params = {"skip": skip, "limit": limit}
        if search:
            params["search"] = search
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/contacts/",
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_contact(self, contact_id: int) -> Dict[str, Any]:
        """Получение контакта по ID"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/contacts/{contact_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_deals(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получение списка сделок"""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/deals/",
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_deal(self, deal_id: int) -> Dict[str, Any]:
        """Получение сделки по ID"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/deals/{deal_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()

