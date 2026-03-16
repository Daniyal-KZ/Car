from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None
    role: str = "user"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None


class UserOut(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
