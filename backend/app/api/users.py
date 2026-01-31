from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import engine
from app.models import User, Base
from app.dependencies import get_db
from app.schemas import UserCreate, UserUpdate, UserOut
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])

# УБРАТЬ эту строку!
# Base.metadata.create_all(bind=engine)

# GET all
@router.get("/", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# GET by id
@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user

# CREATE
@router.post("/", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    # Проверка уникальности email
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already exists")

    # Проверка уникальности username
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username already exists")

    user = User(
        username=data.username,
        email=data.email,
        phone=data.phone,
        role=data.role,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# UPDATE
@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    update_data = data.model_dump(exclude_unset=True)

    # Если обновляется пароль - хешируем его
    if 'password' in update_data:
        update_data['password_hash'] = hash_password(update_data.pop('password'))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

# DELETE
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
    return None