from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)
    password_hash = Column(String, nullable=False)

    cars = relationship("Car", back_populates="owner", cascade="all, delete")



class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    mileage = Column(Float, default=0)
    last_service = Column(Float, default=0)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="cars")
              # Пробег при последнем ТО
