from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    vin = Column(String(17), nullable=True, index=True)
    year = Column(Integer, nullable=False)
    mileage = Column(Float, default=0)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", backref="cars")

    images = relationship("CarImage", back_populates="car", cascade="all, delete-orphan")
