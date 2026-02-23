from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None
    role: str = "user"

class UserCreate(UserBase):
    password: str  # чистый пароль, который мы потом хэшируем

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None  # если меняет

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True

