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
