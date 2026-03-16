from pydantic import BaseModel, ConfigDict
from typing import Optional


class ServiceRequestBase(BaseModel):
    car_id: int
    type: str
    comment: Optional[str] = None


class ServiceRequestCreate(ServiceRequestBase):
    pass


class ServiceRequestUpdate(BaseModel):
    status: Optional[str] = None


class ServiceRequestOut(ServiceRequestBase):
    id: int
    status: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
