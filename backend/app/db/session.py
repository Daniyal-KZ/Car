import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "car_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Keep pool connections healthy after DB/container restarts.
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)

    # Backward-compatible schema patch:
    # some existing databases still have maintenance_rule_tasks.price and
    # do not have maintenance_rule_tasks.unit_price.
    with engine.begin() as conn:
        conn.execute(text("""
            ALTER TABLE IF EXISTS maintenance_rule_tasks
            ADD COLUMN IF NOT EXISTS unit_price DOUBLE PRECISION NOT NULL DEFAULT 0
        """))

        conn.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'maintenance_rule_tasks'
                      AND column_name = 'price'
                ) THEN
                    UPDATE maintenance_rule_tasks
                    SET unit_price = COALESCE(price, 0)
                    WHERE unit_price IS NULL OR unit_price = 0;
                END IF;
            END
            $$;
        """))

        conn.execute(text("""
            ALTER TABLE IF EXISTS users
            ADD COLUMN IF NOT EXISTS ai_api_key_encrypted TEXT
        """))

        conn.execute(text("""
            ALTER TABLE IF EXISTS users
            ADD COLUMN IF NOT EXISTS ai_api_key_masked VARCHAR(32)
        """))

        conn.execute(text("""
            ALTER TABLE IF EXISTS maintenance_rules
            ADD COLUMN IF NOT EXISTS title_i18n JSONB
        """))

        conn.execute(text("""
            ALTER TABLE IF EXISTS maintenance_rules
            ADD COLUMN IF NOT EXISTS notes_i18n JSONB
        """))

        conn.execute(text("""
            ALTER TABLE IF EXISTS maintenance_rule_tasks
            ADD COLUMN IF NOT EXISTS title_i18n JSONB
        """))

        conn.execute(text("""
            ALTER TABLE IF EXISTS maintenance_rule_tasks
            ADD COLUMN IF NOT EXISTS description_i18n JSONB
        """))

        conn.execute(text("""
            ALTER TABLE IF EXISTS service_orders
            ADD COLUMN IF NOT EXISTS service_name_i18n JSONB
        """))

        conn.execute(text("""
            ALTER TABLE IF EXISTS service_orders
            ADD COLUMN IF NOT EXISTS requested_comment_i18n JSONB
        """))

        conn.execute(text("""
            ALTER TABLE IF EXISTS service_orders
            ADD COLUMN IF NOT EXISTS completion_comment_i18n JSONB
        """))

        conn.execute(text("""
            UPDATE maintenance_rules
            SET title_i18n = jsonb_build_object('ru', title)
            WHERE title_i18n IS NULL AND title IS NOT NULL AND title <> ''
        """))

        conn.execute(text("""
            UPDATE maintenance_rules
            SET notes_i18n = jsonb_build_object('ru', notes)
            WHERE notes_i18n IS NULL AND notes IS NOT NULL AND notes <> ''
        """))

        conn.execute(text("""
            UPDATE maintenance_rule_tasks
            SET title_i18n = jsonb_build_object('ru', title)
            WHERE title_i18n IS NULL AND title IS NOT NULL AND title <> ''
        """))

        conn.execute(text("""
            UPDATE maintenance_rule_tasks
            SET description_i18n = jsonb_build_object('ru', description)
            WHERE description_i18n IS NULL AND description IS NOT NULL AND description <> ''
        """))

        conn.execute(text("""
            UPDATE service_orders
            SET service_name_i18n = jsonb_build_object('ru', service_name)
            WHERE service_name_i18n IS NULL AND service_name IS NOT NULL AND service_name <> ''
        """))

        conn.execute(text("""
            UPDATE service_orders
            SET requested_comment_i18n = jsonb_build_object('ru', requested_comment)
            WHERE requested_comment_i18n IS NULL AND requested_comment IS NOT NULL AND requested_comment <> ''
        """))

        conn.execute(text("""
            UPDATE service_orders
            SET completion_comment_i18n = jsonb_build_object('ru', completion_comment)
            WHERE completion_comment_i18n IS NULL AND completion_comment IS NOT NULL AND completion_comment <> ''
        """))


# проверка подключения
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        init_database()
except Exception as e:
    print("Ошибка подключения:", e)
