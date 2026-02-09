from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)

    password_hash = Column(String, nullable=False)

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False, index=True)       # Марка
    model = Column(String, nullable=False, index=True)       # Модель
    year = Column(Integer, nullable=False)                   # Год выпуска
    mileage = Column(Float, default=0)                       # Текущий пробег
    last_service = Column(Float, default=0)                  # Пробег при последнем ТО
