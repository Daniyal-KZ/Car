from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.service_order import EstimateItemIn


class DamageReportImageOut(BaseModel):
    id: int
    report_id: int
    file_path: str
    file_name: str

    model_config = ConfigDict(from_attributes=True)


class DamageReportCreate(BaseModel):
    car_id: int
    title: str
    damage_type: str
    description: Optional[str] = None


class DamageReportAnalyze(BaseModel):
    severity: Optional[str] = None
    mechanic_analysis: str
    recommendation: str
    estimated_cost: Optional[float] = None
    estimate_items: List[EstimateItemIn] = Field(default_factory=list)


class DamageReportCarInfo(BaseModel):
    id: int
    brand: str
    model: str
    year: int

    model_config = ConfigDict(from_attributes=True)


class DamageReportUserInfo(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class DamageReportOut(BaseModel):
    id: int
    car_id: int
    requested_by: int
    service_order_id: Optional[int] = None
    title: str
    damage_type: str
    description: Optional[str] = None
    status: str

    severity: Optional[str] = None
    mechanic_analysis: Optional[str] = None
    recommendation: Optional[str] = None
    estimated_cost: Optional[float] = None

    analyzed_by: Optional[int] = None
    analyzed_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    car: Optional[DamageReportCarInfo] = None
    requester: Optional[DamageReportUserInfo] = None
    analyst: Optional[DamageReportUserInfo] = None
    photos: List[DamageReportImageOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
