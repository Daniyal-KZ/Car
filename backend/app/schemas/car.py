import re

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from app.schemas.user import UserOut
from app.schemas.car_image import CarImageOut


class CarBase(BaseModel):
    brand: str
    model: str
    vin: Optional[str] = None
    year: int
    mileage: float = 0

    @field_validator("vin")
    @classmethod
    def validate_vin(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip().upper()
        if not cleaned:
            return None
        if not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", cleaned):
            raise ValueError("VIN must be 17 chars (A-H, J-N, P, R-Z, 0-9)")
        return cleaned


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    vin: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[float] = None

    @field_validator("vin")
    @classmethod
    def validate_vin(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip().upper()
        if not cleaned:
            return None
        if not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", cleaned):
            raise ValueError("VIN must be 17 chars (A-H, J-N, P, R-Z, 0-9)")
        return cleaned


class CarOut(CarBase):
    id: int
    owner_id: int
    owner: Optional[UserOut] = None
    images: list[CarImageOut] = []

    model_config = ConfigDict(from_attributes=True)
