## SQL схема по моделям `app/models`

Секции ниже можно выполнять по порядку в pgAdmin (Query Tool). Скрипт рассчитан на PostgreSQL 14+.

### 1. Типы и расширения

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'deal_status') THEN
        CREATE TYPE deal_status AS ENUM ('Новая', 'В работе', 'Завершена', 'Отменена');
    END IF;
END $$;
```

### 2. Таблица `users`

```sql
CREATE TABLE IF NOT EXISTS public.users (
    id                SERIAL PRIMARY KEY,
    email             VARCHAR(255) NOT NULL UNIQUE,
    username          VARCHAR(100) NOT NULL UNIQUE,
    full_name         VARCHAR(255) NOT NULL,
    hashed_password   VARCHAR(255) NOT NULL,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser      BOOLEAN NOT NULL DEFAULT FALSE,
    is_verified       BOOLEAN NOT NULL DEFAULT FALSE,
    phone             VARCHAR(20),
    avatar_url        VARCHAR(500),
    timezone          VARCHAR(50) NOT NULL DEFAULT 'UTC',
    language          VARCHAR(10) NOT NULL DEFAULT 'ru',
    preferences       JSONB NOT NULL DEFAULT '{}'::jsonb,
    user_metadata     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ,
    last_login        TIMESTAMPTZ,
    is_deleted        BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at        TIMESTAMPTZ
);
```

### 3. Таблица `companies`

```sql
CREATE TABLE IF NOT EXISTS public.companies (
    id                 SERIAL PRIMARY KEY,
    name               VARCHAR(255) NOT NULL,
    legal_name         VARCHAR(255),
    industry           VARCHAR(100),
    size               VARCHAR(50),
    website            VARCHAR(500),
    email              VARCHAR(255),
    phone              VARCHAR(20),
    fax                VARCHAR(20),
    address_line1      VARCHAR(255),
    address_line2      VARCHAR(255),
    city               VARCHAR(100),
    state              VARCHAR(100),
    postal_code        VARCHAR(20),
    country            VARCHAR(100),
    description        TEXT,
    notes              TEXT,
    status             VARCHAR(50) NOT NULL DEFAULT 'prospect',
    type               VARCHAR(50),
    priority           VARCHAR(20) NOT NULL DEFAULT 'medium',
    owner_id           INTEGER NOT NULL REFERENCES public.users(id),
    parent_company_id  INTEGER REFERENCES public.companies(id),
    custom_fields      JSONB NOT NULL DEFAULT '{}'::jsonb,
    tags               JSONB NOT NULL DEFAULT '[]'::jsonb,
    social_links       JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ,
    last_contacted     TIMESTAMPTZ,
    is_deleted         BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_companies_name  ON public.companies (name);
CREATE INDEX IF NOT EXISTS ix_companies_email ON public.companies (email);
```

### 4. Таблица `contacts`

```sql
CREATE TABLE IF NOT EXISTS public.contacts (
    id               SERIAL PRIMARY KEY,
    first_name       VARCHAR(100) NOT NULL,
    last_name        VARCHAR(100) NOT NULL,
    middle_name      VARCHAR(100),
    email            VARCHAR(255),
    phone            VARCHAR(20),
    job_title        VARCHAR(200),
    department       VARCHAR(200),
    birthday         TIMESTAMPTZ,
    notes            TEXT,
    status           VARCHAR(50) NOT NULL DEFAULT 'lead',
    source           VARCHAR(100),
    priority         VARCHAR(20) NOT NULL DEFAULT 'medium',
    company_id       INTEGER REFERENCES public.companies(id),
    owner_id         INTEGER NOT NULL REFERENCES public.users(id),
    custom_fields    JSONB NOT NULL DEFAULT '{}'::jsonb,
    tags             JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ,
    last_contacted   TIMESTAMPTZ,
    is_deleted       BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at       TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_contacts_email ON public.contacts (email);
CREATE INDEX IF NOT EXISTS ix_contacts_phone ON public.contacts (phone);
```

### 5. Таблица `deals`

```sql
CREATE TABLE IF NOT EXISTS public.deals (
    id                  SERIAL PRIMARY KEY,
    title               VARCHAR(255) NOT NULL,
    description         TEXT,
    amount              NUMERIC(15,2),
    currency            VARCHAR(3) NOT NULL DEFAULT 'RUB',
    probability         INTEGER NOT NULL DEFAULT 0,
    status              deal_status NOT NULL DEFAULT 'Новая',
    expected_close_date TIMESTAMPTZ,
    actual_close_date   TIMESTAMPTZ,
    contact_id          INTEGER REFERENCES public.contacts(id),
    company_id          INTEGER REFERENCES public.companies(id),
    owner_id            INTEGER NOT NULL REFERENCES public.users(id),
    source              VARCHAR(100),
    notes               TEXT,
    custom_fields       JSONB NOT NULL DEFAULT '{}'::jsonb,
    tags                JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at          TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_deals_status     ON public.deals (status);
CREATE INDEX IF NOT EXISTS ix_deals_contact_id ON public.deals (contact_id);
CREATE INDEX IF NOT EXISTS ix_deals_owner_id   ON public.deals (owner_id);
```

### 6. Таблица `activities`

```sql
CREATE TABLE IF NOT EXISTS public.activities (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    type            VARCHAR(50) NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority        VARCHAR(20) NOT NULL DEFAULT 'medium',
    scheduled_at    TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    due_date        TIMESTAMPTZ,
    contact_id      INTEGER REFERENCES public.contacts(id),
    company_id      INTEGER REFERENCES public.companies(id),
    deal_id         INTEGER REFERENCES public.deals(id),
    owner_id        INTEGER NOT NULL REFERENCES public.users(id),
    assigned_to_id  INTEGER REFERENCES public.users(id),
    location        VARCHAR(255),
    duration        INTEGER,
    outcome         TEXT,
    custom_fields   JSONB NOT NULL DEFAULT '{}'::jsonb,
    tags            JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at      TIMESTAMPTZ
);
```

### 7. Таблица `files`

```sql
CREATE TABLE IF NOT EXISTS public.files (
    id                SERIAL PRIMARY KEY,
    filename          VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path         VARCHAR(500) NOT NULL,
    file_url          VARCHAR(500),
    file_size         BIGINT NOT NULL,
    mime_type         VARCHAR(100) NOT NULL,
    file_extension    VARCHAR(10),
    title             VARCHAR(255),
    description       TEXT,
    tags              JSONB NOT NULL DEFAULT '[]'::jsonb,
    contact_id        INTEGER REFERENCES public.contacts(id),
    company_id        INTEGER REFERENCES public.companies(id),
    deal_id           INTEGER REFERENCES public.deals(id),
    activity_id       INTEGER REFERENCES public.activities(id),
    owner_id          INTEGER NOT NULL REFERENCES public.users(id),
    is_public         BOOLEAN NOT NULL DEFAULT FALSE,
    is_encrypted      BOOLEAN NOT NULL DEFAULT FALSE,
    access_level      VARCHAR(50) NOT NULL DEFAULT 'private',
    custom_fields     JSONB NOT NULL DEFAULT '{}'::jsonb,
    file_metadata     JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ,
    is_deleted        BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at        TIMESTAMPTZ
);
```

### 8. Права (опционально)

```sql
GRANT ALL ON ALL TABLES    IN SCHEMA public TO postgres_1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres_1;
```

После выполнения всех блоков база будет соответствовать SQLAlchemy‑моделям. В дальнейшем можно продолжать работать через Alembic или поддерживать схему вручную.***

