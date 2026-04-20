from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class MaintenanceRule(Base):
    __tablename__ = "maintenance_rules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    title_i18n = Column(JSON, nullable=True)
    brand = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    year_from = Column(Integer, nullable=True)
    year_to = Column(Integer, nullable=True)
    mileage_from = Column(Integer, nullable=True)
    mileage_to = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="draft")
    notes = Column(Text, nullable=True)
    notes_i18n = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship(
        "MaintenanceRuleTask",
        back_populates="rule",
        cascade="all, delete-orphan",
        order_by="MaintenanceRuleTask.position"
    )

    executions = relationship(
        "ServiceExecutionLog",
        back_populates="rule",
        cascade="all, delete-orphan",
        order_by="ServiceExecutionLog.created_at.desc()"
    )


class MaintenanceRuleTask(Base):
    __tablename__ = "maintenance_rule_tasks"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("maintenance_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)
    mileage_interval = Column(Integer, nullable=False)  # Пробег в км, на котором выполняется работа
    title = Column(String, nullable=False)
    title_i18n = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    description_i18n = Column(JSON, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    unit_price = Column(Float, nullable=False, default=0)  # Цена за выполнение этой работы

    rule = relationship("MaintenanceRule", back_populates="tasks")
    executions = relationship(
        "ServiceExecutionLog",
        back_populates="task",
        cascade="all, delete-orphan"
    )
