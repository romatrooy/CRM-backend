# Инструкция по миграциям и тестированию модуля "Сделки"

## 📦 Создание и применение миграций

### Вариант 1: Локальная разработка (без Docker)

```bash
# 1. Убедитесь, что база данных запущена и настроена в .env файле
# DATABASE_URL=postgresql://user:password@localhost:5432/crm_db

# 2. Создание новой миграции (автогенерация на основе изменений в моделях)
alembic revision --autogenerate -m "Update Deal model with status enum"

# 3. Проверьте созданный файл миграции в alembic/versions/
# Отредактируйте при необходимости

# 4. Применение миграции
alembic upgrade head

# 5. Проверка текущей версии
alembic current

# 6. Откат миграции (если нужно)
alembic downgrade -1
```

### Вариант 2: С Docker Compose

```bash
# 1. Запустите контейнеры
docker-compose up -d

# 2. Создание миграции
docker-compose exec app alembic revision --autogenerate -m "Update Deal model with status enum"

# 3. Применение миграции
docker-compose exec app alembic upgrade head

# 4. Проверка текущей версии
docker-compose exec app alembic current
```

### Полезные команды Alembic

```bash
# Просмотр истории миграций
alembic history

# Откат к конкретной версии
alembic downgrade <revision_id>

# Откат всех миграций
alembic downgrade base

# Применение следующей миграции
alembic upgrade +1

# Просмотр SQL без выполнения
alembic upgrade head --sql
```

## 🧪 Тестирование эндпоинтов

### Вариант 1: Через Swagger UI (самый простой)

1. Запустите приложение:
   ```bash
   uvicorn app.main:app --reload
   # или
   docker-compose up
   ```

2. Откройте в браузере:
   - **Swagger UI**: http://localhost:8000/api/v1/docs
   - **ReDoc**: http://localhost:8000/api/v1/redoc

3. **Авторизация в Swagger UI:**
   - Найдите кнопку **"Authorize"** (🔒) в правом верхнем углу Swagger UI
   - В открывшемся окне в поле **"Value"** вставьте ваш `access_token` (без слова "Bearer")
   - Нажмите **"Authorize"**, затем **"Close"**
   - Теперь все защищенные эндпоинты будут автоматически использовать этот токен

4. **Получение токена:**
   - Используйте эндпоинт `POST /api/v1/auth/login`
   - В поле `username` введите ваш email
   - В поле `password` введите ваш пароль
   - Скопируйте `access_token` из ответа

5. Тестируйте эндпоинты через интерактивный интерфейс - токен будет автоматически добавляться в заголовок `Authorization: Bearer <token>`

### Вариант 2: Через curl (командная строка)

#### 1. Получение токена авторизации

```bash
# Регистрация пользователя (если еще не зарегистрирован)
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "full_name": "Test User"
  }'

# Вход в систему
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "testpassword123"
  }'

# Сохраните access_token из ответа в переменную
TOKEN="your_access_token_here"
```

#### 2. Создание сделки

```bash
curl -X POST "http://localhost:8000/api/v1/deals/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Продажа программного обеспечения",
    "description": "Продажа CRM системы крупной компании",
    "amount": 500000.00,
    "currency": "RUB",
    "probability": 75,
    "status": "Новая",
    "contact_id": 1,
    "expected_close_date": "2024-12-31T00:00:00"
  }'
```

#### 3. Получение списка сделок

```bash
# Базовый запрос
curl -X GET "http://localhost:8000/api/v1/deals/" \
  -H "Authorization: Bearer $TOKEN"

# С фильтрацией по статусу
curl -X GET "http://localhost:8000/api/v1/deals/?status=Новая" \
  -H "Authorization: Bearer $TOKEN"

# С фильтрацией по менеджеру
curl -X GET "http://localhost:8000/api/v1/deals/?manager_id=1" \
  -H "Authorization: Bearer $TOKEN"

# С фильтрацией по клиенту
curl -X GET "http://localhost:8000/api/v1/deals/?contact_id=1" \
  -H "Authorization: Bearer $TOKEN"

# Комбинированная фильтрация
curl -X GET "http://localhost:8000/api/v1/deals/?status=В%20работе&manager_id=1&contact_id=1" \
  -H "Authorization: Bearer $TOKEN"

# С пагинацией
curl -X GET "http://localhost:8000/api/v1/deals/?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. Получение сделки по ID

```bash
curl -X GET "http://localhost:8000/api/v1/deals/1" \
  -H "Authorization: Bearer $TOKEN"
```

#### 5. Обновление сделки

```bash
curl -X PUT "http://localhost:8000/api/v1/deals/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Обновленное название сделки",
    "amount": 600000.00,
    "probability": 80
  }'
```

#### 6. Изменение статуса сделки

```bash
# Изменение статуса на "В работе"
curl -X PUT "http://localhost:8000/api/v1/deals/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "В работе"
  }'

# Изменение статуса на "Завершена"
curl -X PUT "http://localhost:8000/api/v1/deals/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Завершена"
  }'

# Изменение статуса на "Отменена"
curl -X PUT "http://localhost:8000/api/v1/deals/1/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Отменена"
  }'
```

#### 7. Удаление сделки

```bash
curl -X DELETE "http://localhost:8000/api/v1/deals/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Вариант 3: Через Postman

1. Импортируйте коллекцию или создайте запросы вручную
2. Настройте переменные окружения:
   - `base_url`: `http://localhost:8000/api/v1`
   - `token`: ваш JWT токен
3. Добавьте заголовок авторизации: `Authorization: Bearer {{token}}`

#### Примеры запросов для Postman:

**Создание сделки (POST)**
```
URL: {{base_url}}/deals/
Body (JSON):
{
  "title": "Новая сделка",
  "status": "Новая",
  "contact_id": 1,
  "amount": 100000
}
```

**Изменение статуса (PUT)**
```
URL: {{base_url}}/deals/1/status
Body (JSON):
{
  "status": "В работе"
}
```

**Список сделок с фильтрацией (GET)**
```
URL: {{base_url}}/deals/?status=Новая&manager_id=1
```

### Вариант 4: Автоматические тесты (pytest)

Запуск тестов:

```bash
# Все тесты
pytest

# Только тесты для сделок
pytest tests/test_deals.py

# С подробным выводом
pytest -v tests/test_deals.py

# С покрытием кода
pytest --cov=app --cov-report=html tests/test_deals.py

# Конкретный тест
pytest tests/test_deals.py::TestDeals::test_create_deal
```

## 📝 Примеры тестовых сценариев

### Сценарий 1: Полный жизненный цикл сделки

```bash
# 1. Создание сделки со статусом "Новая"
DEAL_ID=$(curl -s -X POST "http://localhost:8000/api/v1/deals/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Тестовая сделка", "status": "Новая"}' \
  | jq -r '.id')

# 2. Проверка создания
curl -X GET "http://localhost:8000/api/v1/deals/$DEAL_ID" \
  -H "Authorization: Bearer $TOKEN"

# 3. Изменение статуса на "В работе"
curl -X PUT "http://localhost:8000/api/v1/deals/$DEAL_ID/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "В работе"}'

# 4. Проверка обновления updated_at
curl -X GET "http://localhost:8000/api/v1/deals/$DEAL_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.updated_at'

# 5. Завершение сделки
curl -X PUT "http://localhost:8000/api/v1/deals/$DEAL_ID/status" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "Завершена"}'
```

### Сценарий 2: Тестирование фильтрации

```bash
# Создание нескольких сделок с разными статусами
for status in "Новая" "В работе" "Завершена"; do
  curl -X POST "http://localhost:8000/api/v1/deals/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Сделка $status\", \"status\": \"$status\"}"
done

# Фильтрация по статусу "Новая"
curl -X GET "http://localhost:8000/api/v1/deals/?status=Новая" \
  -H "Authorization: Bearer $TOKEN" | jq '.items[] | {id, title, status}'
```

## 🔍 Проверка работы автоматического обновления updated_at

```bash
# 1. Создайте сделку и запомните время создания
DEAL=$(curl -s -X POST "http://localhost:8000/api/v1/deals/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Тест updated_at", "status": "Новая"}')

DEAL_ID=$(echo $DEAL | jq -r '.id')
CREATED_AT=$(echo $DEAL | jq -r '.created_at')
UPDATED_AT=$(echo $DEAL | jq -r '.updated_at')

echo "Создано: $CREATED_AT"
echo "Обновлено: $UPDATED_AT"

# 2. Подождите несколько секунд и обновите сделку
sleep 2

curl -X PUT "http://localhost:8000/api/v1/deals/$DEAL_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Обновленное название"}'

# 3. Проверьте, что updated_at изменился
curl -s -X GET "http://localhost:8000/api/v1/deals/$DEAL_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '{created_at, updated_at}'
```

## ⚠️ Важные замечания

1. **Статусы сделок**: Используйте только следующие значения:
   - `"Новая"`
   - `"В работе"`
   - `"Завершена"`
   - `"Отменена"`

2. **Авторизация**: Все эндпоинты требуют JWT токен в заголовке `Authorization: Bearer <token>`

3. **Кодировка URL**: При использовании кириллицы в параметрах запроса используйте URL-кодирование:
   - `"В работе"` → `"В%20работе"`

4. **Миграции**: Всегда проверяйте созданную миграцию перед применением, особенно при использовании `--autogenerate`

