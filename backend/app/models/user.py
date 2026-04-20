from sqlalchemy import Column, Integer, String, Text
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)
    password_hash = Column(String, nullable=False)
    ai_api_key_encrypted = Column(Text, nullable=True)
    ai_api_key_masked = Column(String(32), nullable=True)

    # Use string reference to avoid circular imports
    cars = None  # Will be set via relationship in Car model
