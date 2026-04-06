from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ServiceBookCreate(BaseModel):
    car_id: int
    type: str
    mileage: int
    description: str
    order_number: Optional[str] = None

class CarInfo(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    mileage: float
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

class ServiceBookOut(BaseModel):
    id: int
    car_id: int
    type: str
    mileage: int
    description: str
    order_number: Optional[str]
    created_at: datetime
    car: Optional[CarInfo] = None

    model_config = ConfigDict(from_attributes=True)