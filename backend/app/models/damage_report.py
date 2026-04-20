from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.db.base import Base


class DamageReport(Base):
    __tablename__ = "damage_reports"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    service_order_id = Column(Integer, ForeignKey("service_orders.id", ondelete="CASCADE"), nullable=True, index=True)

    title = Column(String, nullable=False)
    damage_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="new")

    severity = Column(String, nullable=True)
    mechanic_analysis = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    estimated_cost = Column(Float, nullable=True)

    analyzed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    analyzed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    car = relationship("Car")
    requester = relationship("User", foreign_keys=[requested_by])
    analyst = relationship("User", foreign_keys=[analyzed_by])
    service_order = relationship("ServiceOrder")

    photos = relationship("DamageReportImage", back_populates="report", cascade="all, delete-orphan")


class DamageReportImage(Base):
    __tablename__ = "damage_report_images"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("damage_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)

    report = relationship("DamageReport", back_populates="photos")
