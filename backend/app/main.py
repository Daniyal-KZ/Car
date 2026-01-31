from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import users  # импортируем CRUD

app = FastAPI(title="CAR API")

# CORS
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# подключаем все роуты
app.include_router(users.router)
