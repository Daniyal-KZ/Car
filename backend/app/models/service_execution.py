from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class ServiceExecutionLog(Base):
    __tablename__ = "service_execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("maintenance_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("maintenance_rule_tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    performed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    performed_by_name = Column(String, nullable=False)
    service_type = Column(String, nullable=False, default="maintenance_rule")
    related_object_type = Column(String, nullable=False, default="car")
    related_object_id = Column(Integer, nullable=False, index=True)
    comment = Column(Text, nullable=True)
    performed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    rule = relationship("MaintenanceRule", back_populates="executions")
    task = relationship("MaintenanceRuleTask", back_populates="executions")
    performed_by_user = relationship("User")
