from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InvoiceItemOut(BaseModel):
    id: int
    title: str
    quantity: float
    unit_price: float
    total_price: float

    model_config = ConfigDict(from_attributes=True)


class InvoiceItemUpdate(BaseModel):
    title: str
    quantity: float = 1
    unit_price: float = 0


class InvoiceOrderSummary(BaseModel):
    id: int
    service_name: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class InvoiceOut(BaseModel):
    id: int
    order_id: int
    invoice_number: str
    status: str
    currency: str
    subtotal: float
    total: float
    created_at: datetime
    paid_at: datetime | None = None
    items: List[InvoiceItemOut] = Field(default_factory=list)
    order: Optional[InvoiceOrderSummary] = None

    model_config = ConfigDict(from_attributes=True)


class InvoiceAdminUpdate(BaseModel):
    items: List[InvoiceItemUpdate] = Field(default_factory=list)
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
