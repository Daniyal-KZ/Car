from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class ServiceOrder(Base):
    __tablename__ = "service_orders"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    service_kind = Column(String, nullable=False, default="other_service")
    service_name = Column(String, nullable=False)
    service_name_i18n = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="new")

    requested_comment = Column(Text, nullable=True)
    requested_comment_i18n = Column(JSON, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)

    accepted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    completion_comment = Column(Text, nullable=True)
    completion_comment_i18n = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    car = relationship("Car")
    requester = relationship("User", foreign_keys=[requested_by])
    mechanic = relationship("User", foreign_keys=[accepted_by])
    invoice = relationship("Invoice", back_populates="order", uselist=False, cascade="all, delete-orphan")
