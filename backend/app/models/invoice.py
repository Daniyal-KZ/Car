from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("service_orders.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    invoice_number = Column(String, nullable=False, unique=True, index=True)
    status = Column(String, nullable=False, default="unpaid")
    currency = Column(String, nullable=False, default="KZT")

    subtotal = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

    order = relationship("ServiceOrder", back_populates="invoice")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String, nullable=False)
    quantity = Column(Float, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0)
    total_price = Column(Float, nullable=False, default=0)

    invoice = relationship("Invoice", back_populates="items")
