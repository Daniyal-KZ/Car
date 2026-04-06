from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class ServiceBookEntry(Base):
    __tablename__ = "service_book_entries"

    id = Column(Integer, primary_key=True, index=True)

    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)

    type = Column(String, nullable=False)

    mileage = Column(Integer, nullable=False)
    description = Column(String, nullable=False)

    order_number = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    car = relationship("Car", backref="service_entries")