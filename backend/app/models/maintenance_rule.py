from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class MaintenanceRule(Base):
    __tablename__ = "maintenance_rules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    brand = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    year_from = Column(Integer, nullable=True)
    year_to = Column(Integer, nullable=True)
    mileage_from = Column(Integer, nullable=True)
    mileage_to = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="draft")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship(
        "MaintenanceRuleTask",
        back_populates="rule",
        cascade="all, delete-orphan",
        order_by="MaintenanceRuleTask.position"
    )


class MaintenanceRuleTask(Base):
    __tablename__ = "maintenance_rule_tasks"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("maintenance_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)
    mileage_interval = Column(Integer, nullable=False)  # Пробег в км, на котором выполняется работа
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    rule = relationship("MaintenanceRule", back_populates="tasks")
