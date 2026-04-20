from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceRuleTaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    mileage_interval: int
    duration_minutes: Optional[int] = None
    unit_price: float = 0

    model_config = ConfigDict(from_attributes=True)


class MaintenanceRuleOut(BaseModel):
    id: int
    title: str
    tasks: List[MaintenanceRuleTaskOut] = []

    model_config = ConfigDict(from_attributes=True)


class EstimateItemIn(BaseModel):
    title: str
    quantity: float = 1
    unit_price: float = 0
    task_id: Optional[int] = None


class ServiceOrderCreate(BaseModel):
    car_id: int
    service_name: str
    service_name_i18n: Optional[dict[str, str]] = None
    service_kind: Optional[str] = None
    requested_comment: Optional[str] = None
    requested_comment_i18n: Optional[dict[str, str]] = None
    scheduled_at: Optional[datetime] = None


class ServiceOrderAccept(BaseModel):
    comment: Optional[str] = None


class ServiceOrderComplete(BaseModel):
    completion_comment: Optional[str] = None
    completion_comment_i18n: Optional[dict[str, str]] = None
    estimate_items: List[EstimateItemIn] = Field(default_factory=list)


class ServiceOrderOut(BaseModel):
    id: int
    car_id: int
    requested_by: int
    service_kind: str
    service_name: str
    service_name_i18n: Optional[dict[str, str]] = None
    status: str
    requested_comment: Optional[str] = None
    requested_comment_i18n: Optional[dict[str, str]] = None
    scheduled_at: Optional[datetime] = None
    accepted_by: Optional[int] = None
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    completion_comment: Optional[str] = None
    completion_comment_i18n: Optional[dict[str, str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ServiceOrderCarInfo(BaseModel):
    id: int
    brand: str
    model: str
    vin: str | None = None
    year: int
    mileage: float

    model_config = ConfigDict(from_attributes=True)


class ServiceOrderUserInfo(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class ServiceOrderDetailsOut(ServiceOrderOut):
    car: ServiceOrderCarInfo | None = None
    requester: ServiceOrderUserInfo | None = None
    mechanic: ServiceOrderUserInfo | None = None
    maintenance_rule: MaintenanceRuleOut | None = None

    model_config = ConfigDict(from_attributes=True)
