"""Update Deal model with status enum

Revision ID: d0b15559b077
Revises: 5a17a119abb9
Create Date: 2025-11-08 06:27:29.729294

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd0b15559b077'
down_revision = '5a17a119abb9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем ENUM тип, если его еще нет
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE dealstatus AS ENUM ('NEW', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Удаляем индексы, если они существуют (для безопасности)
    op.execute("DROP INDEX IF EXISTS ix_deals_status")
    op.execute("DROP INDEX IF EXISTS ix_deals_contact_id")
    op.execute("DROP INDEX IF EXISTS ix_deals_owner_id")
    
    # Преобразуем существующие строковые значения в значения, соответствующие ENUM
    # Маппинг старых значений на новые значения ENUM (как строки)
    op.execute("""
        UPDATE deals 
        SET status = CASE 
            WHEN status = 'open' OR status = 'Новая' THEN 'NEW'
            WHEN status = 'won' OR status = 'В работе' THEN 'IN_PROGRESS'
            WHEN status = 'closed_won' OR status = 'Завершена' THEN 'COMPLETED'
            WHEN status = 'lost' OR status = 'cancelled' OR status = 'Отменена' THEN 'CANCELLED'
            ELSE 'NEW'
        END
        WHERE status IS NOT NULL
    """)
    
    # Устанавливаем значения по умолчанию для NULL
    op.execute("UPDATE deals SET status = 'NEW' WHERE status IS NULL")
    
    # Изменяем тип колонки с использованием USING для преобразования строки в ENUM
    op.execute("""
        ALTER TABLE deals 
        ALTER COLUMN status TYPE dealstatus 
        USING status::dealstatus
    """)
    
    # Устанавливаем NOT NULL
    op.execute("ALTER TABLE deals ALTER COLUMN status SET NOT NULL")
    
    # Создаем индексы
    op.create_index(op.f('ix_deals_contact_id'), 'deals', ['contact_id'], unique=False)
    op.create_index(op.f('ix_deals_owner_id'), 'deals', ['owner_id'], unique=False)
    op.create_index(op.f('ix_deals_status'), 'deals', ['status'], unique=False)
    
    # Удаляем колонку stage
    op.drop_column('deals', 'stage')


def downgrade() -> None:
    # Добавляем колонку stage обратно
    op.add_column('deals', sa.Column('stage', sa.VARCHAR(length=100), autoincrement=False, nullable=False, server_default='qualification'))
    
    # Удаляем индексы
    op.drop_index(op.f('ix_deals_status'), table_name='deals')
    op.drop_index(op.f('ix_deals_owner_id'), table_name='deals')
    op.drop_index(op.f('ix_deals_contact_id'), table_name='deals')
    
    # Преобразуем ENUM обратно в VARCHAR
    op.execute("""
        ALTER TABLE deals 
        ALTER COLUMN status TYPE VARCHAR(50) 
        USING CASE status::text
            WHEN 'NEW' THEN 'open'
            WHEN 'IN_PROGRESS' THEN 'won'
            WHEN 'COMPLETED' THEN 'closed_won'
            WHEN 'CANCELLED' THEN 'cancelled'
            ELSE 'open'
        END
    """)
    
    # Устанавливаем nullable
    op.execute("ALTER TABLE deals ALTER COLUMN status DROP NOT NULL")
    
    # Удаляем ENUM тип
    op.execute("DROP TYPE IF EXISTS dealstatus")
