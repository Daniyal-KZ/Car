from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class AssistantChat(Base):
    __tablename__ = "assistant_chats"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False, default="Новый чат")
    provider = Column(String, nullable=False, default="gemini")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User")
    messages = relationship(
        "AssistantMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="AssistantMessage.created_at.asc()",
    )
