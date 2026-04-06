from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceTaskBase(BaseModel):
    mileage_interval: int  # Пробег в км, на котором выполняется работа
    title: str
    description: Optional[str] = None
    duration_minutes: Optional[int] = None


class MaintenanceTaskCreate(MaintenanceTaskBase):
    position: Optional[int] = None


class MaintenanceTaskOut(MaintenanceTaskBase):
    id: int
    position: int

    model_config = ConfigDict(from_attributes=True)


class MaintenanceRuleBase(BaseModel):
    title: str
    brand: str
    model: str
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    mileage_from: Optional[int] = None
    mileage_to: Optional[int] = None
    status: str = "draft"
    notes: Optional[str] = None
    tasks: List[MaintenanceTaskCreate] = Field(default_factory=list)


class MaintenanceRuleCreate(MaintenanceRuleBase):
    pass


class MaintenanceRuleUpdate(BaseModel):
    title: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    mileage_from: Optional[int] = None
    mileage_to: Optional[int] = None
    status: Optional[str] = None
    duration_minutes: Optional[int] = None
    price: Optional[float] = None
    notes: Optional[str] = None
    tasks: Optional[List[MaintenanceTaskCreate]] = None


class MaintenanceRuleOut(BaseModel):
    id: int
    title: str
    brand: str
    model: str
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    mileage_from: Optional[int] = None
    mileage_to: Optional[int] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tasks: List[MaintenanceTaskOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class MaintenanceRuleForCarOut(BaseModel):
    id: int
    title: str
    brand: str
    model: str
    status: str
    tasks: List[MaintenanceTaskOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
