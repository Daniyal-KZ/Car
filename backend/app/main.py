import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "car_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# создаём движок SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Проверка соединения
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("✅ Подключение к Postgres успешно!")
except Exception as e:
    print("❌ Ошибка подключения:", e)

# Инициализация FastAPI
app = FastAPI(title="CAR API")

# CORS — разрешаем Nuxt на localhost:3000
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# создаём таблицу users
with engine.begin() as conn:
    conn.execute(text("""
                      CREATE TABLE IF NOT EXISTS users (
                                                           id SERIAL PRIMARY KEY,
                                                           username VARCHAR(50) NOT NULL,
                          role VARCHAR(20) NOT NULL
                          );
                      """))

# Seed три тестовых юзера
def seed_users():
    with engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        if count == 0:
            conn.execute(text("""
                              INSERT INTO users (username, role) VALUES
                                                                     ('admin', 'ADMIN'),
                                                                     ('developer', 'DEVELOPER'),
                                                                     ('user', 'USER')
                              """))
            print("✅ Seed: 3 test users created")
        else:
            print("ℹ️ Users already exist, skipping seed")

seed_users()

# Роуты
@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/users")
def get_users():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users"))
        users = [dict(row._mapping) for row in result]
    return {"users": users}

@app.post("/users/add")
def add_user(username: str, role: str):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO users (username, role) VALUES (:username, :role)"),
            {"username": username, "role": role}
        )
    return {"status": "user added", "username": username, "role": role}
