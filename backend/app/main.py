from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .db import engine

app = FastAPI(title="CAR API")

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
