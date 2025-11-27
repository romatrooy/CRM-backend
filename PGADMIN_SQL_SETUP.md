## Настройка базы через pgAdmin

Ниже — готовые блоки SQL, которые можно выполнить в **Query Tool** pgAdmin, чтобы подготовить отдельную базу `crm-backend` под подключение `postgresql+psycopg2://postgres_1:Password123@localhost:5432/crm-backend`.

### 1. Создать пользователя и базу

> Запускай в любом подключении к `postgres` (или другой системной базе).

```sql
DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'postgres_1'
    ) THEN
        CREATE ROLE postgres_1
            LOGIN
            PASSWORD 'Password123';
    END IF;
END
$$;

SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'crm-backend';

DROP DATABASE IF EXISTS "crm-backend";

CREATE DATABASE "crm-backend"
    WITH OWNER = postgres_1
         ENCODING = 'UTF8'
         TEMPLATE = template0
         CONNECTION LIMIT = -1;
```

### 2. Подключиться к новой базе

В pgAdmin просто выбери базу **crm-backend** в выпадающем списке Query Tool (команда `\c` не нужна).

### 3. Расширения и search_path

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

ALTER ROLE postgres_1 IN DATABASE "crm-backend"
    SET search_path = public;
```

### 4. Минимальные структуры (опционально)

Если нужно просто проверить подключение до Alembic, можно создать “заглушки” схемы:

```sql
CREATE SCHEMA IF NOT EXISTS public AUTHORIZATION postgres_1;
GRANT ALL ON SCHEMA public TO postgres_1;
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres_1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres_1;
```

### 5. Дальше

1. Активируй виртуальное окружение и установи `DATABASE_URL=postgresql+psycopg2://postgres_1:Password123@localhost:5432/crm-backend`.
2. Выполни `alembic upgrade head`, чтобы накатить миграции и построить всю схему.
3. После генерации ERD верни старую строку подключения в `.env`, перезапусти сервисы Docker при необходимости.

Теперь все действия в pgAdmin ограничиваются запуском этих SQL‑скриптов; реальное продакшен‑окружение при этом не затрагивается.

