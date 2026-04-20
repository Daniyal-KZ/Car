import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api import users, auth, cars, service_book, maintenance_rules, service_orders, invoices, damage_reports, assistant
from app.db.base import Base
from app.db.session import engine

app = FastAPI(title="CAR API")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/cars", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(service_book.router)
app.include_router(maintenance_rules.router)
app.include_router(service_orders.router)
app.include_router(invoices.router)
app.include_router(damage_reports.router)
app.include_router(assistant.router)

Base.metadata.create_all(bind=engine)

# Lightweight schema backfill for existing DBs without manual migrations.
with engine.begin() as connection:
    connection.execute(text("ALTER TABLE cars ADD COLUMN IF NOT EXISTS vin VARCHAR(17)"))