"""
Тесты для сделок
"""
import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.models.deal import DealStatus


class TestDeals:
    """Тесты для работы со сделками"""
    
    def test_create_deal(self, client: TestClient, test_user):
        """Тест создания сделки"""
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        deal_data = {
            "title": "Продажа CRM системы",
            "description": "Продажа CRM системы крупной компании",
            "amount": 500000.00,
            "currency": "RUB",
            "probability": 75,
            "status": "Новая",
            "contact_id": None,
            "expected_close_date": None
        }
        
        response = client.post("/api/v1/deals/", json=deal_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == deal_data["title"]
        assert data["status"] == DealStatus.NEW.value
        assert data["owner_id"] == test_user.id
        assert data["amount"] == str(deal_data["amount"])
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_get_deals(self, client: TestClient, test_user):
        """Тест получения списка сделок"""
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/deals/", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_get_deals_with_status_filter(self, client: TestClient, test_user, db_session):
        """Тест фильтрации сделок по статусу"""
        from app.models.deal import Deal
        
        # Создание тестовых сделок с разными статусами
        deal1 = Deal(
            title="Сделка 1",
            status=DealStatus.NEW,
            owner_id=test_user.id
        )
        deal2 = Deal(
            title="Сделка 2",
            status=DealStatus.IN_PROGRESS,
            owner_id=test_user.id
        )
        db_session.add(deal1)
        db_session.add(deal2)
        await db_session.commit()
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Фильтрация по статусу "Новая"
        response = client.get("/api/v1/deals/?status=Новая", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "Новая" for item in data["items"])
    
    @pytest.mark.asyncio
    async def test_get_deals_with_manager_filter(self, client: TestClient, test_user, db_session):
        """Тест фильтрации сделок по менеджеру"""
        from app.models.deal import Deal
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Создание второго пользователя
        manager2 = User(
            email="manager2@example.com",
            username="manager2",
            full_name="Manager 2",
            hashed_password=get_password_hash("password"),
            is_active=True
        )
        db_session.add(manager2)
        await db_session.commit()
        await db_session.refresh(manager2)
        
        # Создание сделок для разных менеджеров
        deal1 = Deal(title="Сделка менеджера 1", owner_id=test_user.id, status=DealStatus.NEW)
        deal2 = Deal(title="Сделка менеджера 2", owner_id=manager2.id, status=DealStatus.NEW)
        db_session.add(deal1)
        db_session.add(deal2)
        await db_session.commit()
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Фильтрация по менеджеру
        response = client.get(f"/api/v1/deals/?manager_id={test_user.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert all(item["owner_id"] == test_user.id for item in data["items"])
    
    @pytest.mark.asyncio
    async def test_get_deals_with_contact_filter(self, client: TestClient, test_user, db_session):
        """Тест фильтрации сделок по клиенту"""
        from app.models.deal import Deal
        from app.models.contact import Contact
        
        # Создание контакта
        contact = Contact(
            first_name="Test",
            last_name="Contact",
            email="test@example.com",
            owner_id=test_user.id
        )
        db_session.add(contact)
        await db_session.commit()
        await db_session.refresh(contact)
        
        # Создание сделок
        deal1 = Deal(title="Сделка 1", contact_id=contact.id, owner_id=test_user.id, status=DealStatus.NEW)
        deal2 = Deal(title="Сделка 2", contact_id=None, owner_id=test_user.id, status=DealStatus.NEW)
        db_session.add(deal1)
        db_session.add(deal2)
        await db_session.commit()
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Фильтрация по клиенту
        response = client.get(f"/api/v1/deals/?contact_id={contact.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert all(item["contact_id"] == contact.id for item in data["items"])
    
    @pytest.mark.asyncio
    async def test_get_deal_by_id(self, client: TestClient, test_user, db_session):
        """Тест получения сделки по ID"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Тестовая сделка",
            status=DealStatus.NEW,
            owner_id=test_user.id
        )
        db_session.add(deal)
        await db_session.commit()
        await db_session.refresh(deal)
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/api/v1/deals/{deal.id}", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == deal.id
        assert data["title"] == deal.title
        assert data["status"] == DealStatus.NEW.value
    
    @pytest.mark.asyncio
    async def test_update_deal(self, client: TestClient, test_user, db_session):
        """Тест обновления сделки"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Тестовая сделка",
            status=DealStatus.NEW,
            owner_id=test_user.id
        )
        db_session.add(deal)
        await db_session.commit()
        await db_session.refresh(deal)
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        update_data = {
            "title": "Обновленное название",
            "amount": 600000.00,
            "probability": 80
        }
        
        response = client.put(f"/api/v1/deals/{deal.id}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["amount"] == str(update_data["amount"])
        assert data["probability"] == update_data["probability"]
        # Проверка, что updated_at обновился
        assert data["updated_at"] is not None
    
    @pytest.mark.asyncio
    async def test_update_deal_status(self, client: TestClient, test_user, db_session):
        """Тест изменения статуса сделки"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Тестовая сделка",
            status=DealStatus.NEW,
            owner_id=test_user.id
        )
        db_session.add(deal)
        await db_session.commit()
        await db_session.refresh(deal)
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Изменение статуса на "В работе"
        status_update = {"status": "В работе"}
        response = client.put(f"/api/v1/deals/{deal.id}/status", json=status_update, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == DealStatus.IN_PROGRESS.value
        
        # Изменение статуса на "Завершена"
        status_update = {"status": "Завершена"}
        response = client.put(f"/api/v1/deals/{deal.id}/status", json=status_update, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == DealStatus.COMPLETED.value
    
    @pytest.mark.asyncio
    async def test_update_deal_status_all_statuses(self, client: TestClient, test_user, db_session):
        """Тест всех возможных статусов"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Тестовая сделка",
            status=DealStatus.NEW,
            owner_id=test_user.id
        )
        db_session.add(deal)
        await db_session.commit()
        await db_session.refresh(deal)
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Тестирование всех статусов
        statuses = [
            ("Новая", DealStatus.NEW),
            ("В работе", DealStatus.IN_PROGRESS),
            ("Завершена", DealStatus.COMPLETED),
            ("Отменена", DealStatus.CANCELLED)
        ]
        
        for status_str, status_enum in statuses:
            response = client.put(
                f"/api/v1/deals/{deal.id}/status",
                json={"status": status_str},
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == status_enum.value
    
    @pytest.mark.asyncio
    async def test_delete_deal(self, client: TestClient, test_user, db_session):
        """Тест удаления сделки"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Тестовая сделка",
            status=DealStatus.NEW,
            owner_id=test_user.id
        )
        db_session.add(deal)
        await db_session.commit()
        await db_session.refresh(deal)
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete(f"/api/v1/deals/{deal.id}", headers=headers)
        assert response.status_code == 204
        
        # Проверка, что сделка не возвращается в списке
        response = client.get("/api/v1/deals/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert not any(item["id"] == deal.id for item in data["items"])
    
    @pytest.mark.asyncio
    async def test_auto_update_updated_at(self, client: TestClient, test_user, db_session):
        """Тест автоматического обновления updated_at"""
        from app.models.deal import Deal
        import asyncio
        
        deal = Deal(
            title="Тестовая сделка",
            status=DealStatus.NEW,
            owner_id=test_user.id
        )
        db_session.add(deal)
        await db_session.commit()
        await db_session.refresh(deal)
        
        original_updated_at = deal.updated_at
        
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Ждем немного, чтобы время точно изменилось
        await asyncio.sleep(1)
        
        # Обновляем сделку
        response = client.put(
            f"/api/v1/deals/{deal.id}",
            json={"title": "Обновленное название"},
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # Проверяем, что updated_at изменился
        assert data["updated_at"] is not None
        assert data["updated_at"] != original_updated_at
    
    def test_deal_not_found(self, client: TestClient, test_user):
        """Тест получения несуществующей сделки"""
        token = create_access_token({"sub": str(test_user.id), "username": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/deals/99999", headers=headers)
        assert response.status_code == 404
    
    def test_unauthorized_access(self, client: TestClient):
        """Тест доступа без авторизации"""
        response = client.get("/api/v1/deals/")
        assert response.status_code == 401

