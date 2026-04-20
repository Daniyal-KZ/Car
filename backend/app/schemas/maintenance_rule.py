from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MaintenanceTaskBase(BaseModel):
    mileage_interval: int  # Пробег в км, на котором выполняется работа
    title: str
    title_i18n: Optional[dict[str, str]] = None
    description: Optional[str] = None
    description_i18n: Optional[dict[str, str]] = None
    duration_minutes: Optional[int] = None
    unit_price: float = 0  # Цена за выполнение этой работы


class MaintenanceTaskCreate(MaintenanceTaskBase):
    position: Optional[int] = None


class ServiceExecutionBase(BaseModel):
    task_id: Optional[int] = None
    related_object_type: str = "car"
    related_object_id: int
    comment: Optional[str] = None


class ServiceExecutionCreate(ServiceExecutionBase):
    pass


class ServiceExecutionOut(ServiceExecutionBase):
    id: int
    rule_id: int
    performed_by: Optional[int] = None
    performed_by_username: Optional[str] = None
    performed_by_name: Optional[str] = None
    performed_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MaintenanceTaskOut(MaintenanceTaskBase):
    id: int
    position: int

    model_config = ConfigDict(from_attributes=True)


class MaintenanceRuleBase(BaseModel):
    title: str
    title_i18n: Optional[dict[str, str]] = None
    brand: str
    model: str
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    mileage_from: Optional[int] = None
    mileage_to: Optional[int] = None
    status: str = "draft"
    notes: Optional[str] = None
    notes_i18n: Optional[dict[str, str]] = None
    tasks: List[MaintenanceTaskCreate] = Field(default_factory=list)


class MaintenanceRuleCreate(MaintenanceRuleBase):
    pass


class MaintenanceRuleUpdate(BaseModel):
    title: Optional[str] = None
    title_i18n: Optional[dict[str, str]] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    mileage_from: Optional[int] = None
    mileage_to: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    notes_i18n: Optional[dict[str, str]] = None
    tasks: Optional[List[MaintenanceTaskCreate]] = None


class MaintenanceRuleOut(BaseModel):
    id: int
    title: str
    title_i18n: Optional[dict[str, str]] = None
    brand: str
    model: str
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    mileage_from: Optional[int] = None
    mileage_to: Optional[int] = None
    status: str
    notes: Optional[str] = None
    notes_i18n: Optional[dict[str, str]] = None
    created_at: datetime
    updated_at: datetime
    tasks: List[MaintenanceTaskOut] = Field(default_factory=list)
    last_execution_at: Optional[datetime] = None
    last_execution_by: Optional[str] = None
    execution_status: Optional[str] = None
    executions: List[ServiceExecutionOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class MaintenanceRuleForCarOut(BaseModel):
    id: int
    title: str
    title_i18n: Optional[dict[str, str]] = None
    brand: str
    model: str
    status: str
    tasks: List[MaintenanceTaskOut] = Field(default_factory=list)
    last_execution_at: Optional[datetime] = None
    last_execution_by: Optional[str] = None
    execution_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
