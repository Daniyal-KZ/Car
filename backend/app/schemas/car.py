from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.user import UserOut
from app.schemas.car_image import CarImageOut


class CarBase(BaseModel):
    brand: str
    model: str
    year: int
    mileage: float = 0


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[float] = None
    last_service: Optional[float] = None


class CarOut(CarBase):
    id: int
    last_service: float
    owner_id: int
    owner: Optional[UserOut] = None
    images: list[CarImageOut] = []

    model_config = ConfigDict(from_attributes=True)
