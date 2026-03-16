from sqlalchemy import Column, Integer, String
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)
    password_hash = Column(String, nullable=False)

    # Use string reference to avoid circular imports
    cars = None  # Will be set via relationship in Car model
