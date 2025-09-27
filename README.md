# CRM Backend

Бэкенд для CRM системы, построенный на FastAPI, PostgreSQL и Redis.

## Технологический стек

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **База данных**: PostgreSQL с поддержкой JSONB
- **Кеширование**: Redis
- **Фоновые задачи**: Celery
- **Аутентификация**: JWT токены
- **Контейнеризация**: Docker, Docker Compose
- **Тестирование**: pytest, TestClient

## Структура проекта

```
CRM-backend/
├── app/                          # Основное приложение
│   ├── api/                      # API роутеры
│   │   └── v1/
│   │       ├── api.py           # Главный роутер API v1
│   │       └── endpoints/        # Эндпоинты
│   │           ├── auth.py      # Аутентификация
│   │           ├── users.py     # Пользователи
│   │           ├── contacts.py  # Контакты
│   │           ├── companies.py # Компании
│   │           ├── deals.py         # Сделки
│   │           ├── activities.py # Активности
│   │           └── files.py    # Файлы
│   ├── core/                     # Основные модули
│   │   ├── config.py           # Конфигурация
│   │   ├── database.py         # Настройка БД
│   │   ├── security.py         # Безопасность
│   │   └── celery.py           # Celery настройки
│   ├── models/                   # Модели SQLAlchemy
│   │   ├── user.py             # Пользователи
│   │   ├── contact.py          # Контакты
│   │   ├── company.py          # Компании
│   │   ├── deal.py             # Сделки
│   │   ├── activity.py         # Активности
│   │   └── file.py             # Файлы
│   ├── schemas/                  # Pydantic схемы
│   │   ├── user.py             # Схемы пользователей
│   │   ├── contact.py          # Схемы контактов
│   │   ├── company.py          # Схемы компаний
│   │   ├── deal.py             # Схемы сделок
│   │   ├── activity.py         # Схемы активностей
│   │   └── file.py             # Схемы файлов
│   ├── services/                 # Бизнес-логика
│   │   ├── user_service.py     # Сервис пользователей
│   │   ├── contact_service.py  # Сервис контактов
│   │   ├── company_service.py  # Сервис компаний
│   │   ├── deal_service.py     # Сервис сделок
│   │   ├── activity_service.py # Сервис активностей
│   │   └── file_service.py     # Сервис файлов
│   ├── tasks/                    # Celery задачи
│   │   ├── email.py            # Email задачи
│   │   ├── import_export.py    # Импорт/экспорт
│   │   ├── reports.py          # Отчеты
│   │   ├── notifications.py    # Уведомления
│   │   └── cleanup.py          # Очистка данных
│   └── main.py                  # Точка входа
├── alembic/                      # Миграции БД
│   ├── env.py                  # Настройка Alembic
│   ├── script.py.mako          # Шаблон миграций
│   └── versions/               # Файлы миграций
├── tests/                       # Тесты
│   ├── conftest.py             # Конфигурация тестов
│   ├── test_auth.py            # Тесты аутентификации
│   └── test_contacts.py        # Тесты контактов
├── requirements.txt             # Python зависимости
├── env.example                  # Пример переменных окружения
├── docker-compose.yml           # Docker Compose
├── Dockerfile                   # Docker образ
├── alembic.ini                 # Конфигурация Alembic
├── pytest.ini                  # Конфигурация pytest
└── README.md                    # Документация
```

## Быстрый старт

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd CRM-backend
```

### 2. Настройка переменных окружения

```bash
cp env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 4. Инициализация базы данных

```bash
# Создание миграций
docker-compose exec app alembic revision --autogenerate -m "Initial migration"

# Применение миграций
docker-compose exec app alembic upgrade head
```

### 5. Доступ к приложению

- **API**: http://localhost:8000
- **Документация**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## Разработка

### Локальная разработка без Docker

1. Установите Python 3.11+
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте PostgreSQL и Redis локально

5. Запустите приложение:
   ```bash
   uvicorn app.main:app --reload
   ```

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием кода
pytest --cov=app --cov-report=html

# Конкретный тест
pytest tests/test_auth.py::TestAuth::test_register_user
```

### Создание миграций

```bash
# Создание новой миграции
alembic revision --autogenerate -m "Description of changes"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## API Endpoints

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация пользователя
- `POST /api/v1/auth/login` - Вход в систему
- `POST /api/v1/auth/refresh` - Обновление токена

### Пользователи
- `GET /api/v1/users/me` - Текущий пользователь
- `PUT /api/v1/users/me` - Обновление профиля

### Контакты
- `GET /api/v1/contacts/` - Список контактов
- `POST /api/v1/contacts/` - Создание контакта
- `GET /api/v1/contacts/{id}` - Получение контакта
- `PUT /api/v1/contacts/{id}` - Обновление контакта
- `DELETE /api/v1/contacts/{id}` - Удаление контакта

### Компании
- `GET /api/v1/companies/` - Список компаний
- `POST /api/v1/companies/` - Создание компании
- `GET /api/v1/companies/{id}` - Получение компании
- `PUT /api/v1/companies/{id}` - Обновление компании
- `DELETE /api/v1/companies/{id}` - Удаление компании

### Сделки
- `GET /api/v1/deals/` - Список сделок
- `POST /api/v1/deals/` - Создание сделки
- `GET /api/v1/deals/{id}` - Получение сделки
- `PUT /api/v1/deals/{id}` - Обновление сделки
- `DELETE /api/v1/deals/{id}` - Удаление сделки

### Активности
- `GET /api/v1/activities/` - Список активностей
- `POST /api/v1/activities/` - Создание активности
- `GET /api/v1/activities/{id}` - Получение активности
- `PUT /api/v1/activities/{id}` - Обновление активности
- `DELETE /api/v1/activities/{id}` - Удаление активности

### Файлы
- `GET /api/v1/files/` - Список файлов
- `POST /api/v1/files/upload` - Загрузка файла
- `GET /api/v1/files/{id}` - Получение файла
- `DELETE /api/v1/files/{id}` - Удаление файла

## Особенности архитектуры

### Модели данных
- **Пользователи**: Управление пользователями системы
- **Контакты**: Лиды, клиенты, партнеры
- **Компании**: Организации и компании
- **Сделки**: Sales pipeline и opportunities
- **Активности**: Взаимодействия, задачи, встречи
- **Файлы**: Вложения и документы

### Безопасность
- JWT токены для аутентификации
- Хеширование паролей с bcrypt
- Мягкое удаление записей
- Валидация данных с Pydantic

### Производительность
- Асинхронные операции с базой данных
- Кеширование с Redis
- Фоновые задачи с Celery
- Пагинация для больших списков

### Масштабируемость
- Микросервисная архитектура
- Контейнеризация с Docker
- Горизонтальное масштабирование
- Разделение на слои (API, Services, Models)

## Мониторинг и логирование

- Структурированные логи с structlog
- Health check endpoints
- Метрики производительности
- Обработка ошибок

## Развертывание

### Production
1. Настройте production переменные окружения
2. Используйте production базу данных
3. Настройте reverse proxy (Nginx)
4. Настройте SSL сертификаты
5. Настройте мониторинг и логирование

### CI/CD
- GitHub Actions для автоматического тестирования
- Docker registry для образов
- Автоматическое развертывание
- Rollback стратегии

## Лицензия

MIT License
