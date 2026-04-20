from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserOut
from app.core.security import hash_password, encrypt_secret
from app.api.auth import get_current_user
from app.api.deps import require_roles

router = APIRouter(prefix="/users", tags=["users"])


class UserAiKeyUpdate(BaseModel):
    api_key: str


class UserAiKeyStatus(BaseModel):
    has_key: bool
    masked_key: str | None = None


def _mask_api_key(api_key: str) -> str:
    trimmed = api_key.strip()
    if len(trimmed) <= 8:
        return "****"
    return f"{trimmed[:4]}...{trimmed[-4:]}"

# ✅ GET all — только admin/dev
@router.get("/", response_model=list[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "dev"))
):
    return db.query(User).all()

# ✅ GET текущего пользователя — возвращаем pydantic модель
@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.get("/me/ai-key", response_model=UserAiKeyStatus)
def get_my_ai_key_status(current_user: User = Depends(get_current_user)):
    return UserAiKeyStatus(
        has_key=bool(current_user.ai_api_key_encrypted),
        masked_key=current_user.ai_api_key_masked,
    )


@router.put("/me/ai-key", response_model=UserAiKeyStatus)
def save_my_ai_key(
    payload: UserAiKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api_key = payload.api_key.strip()
    if len(api_key) < 10:
        raise HTTPException(status_code=400, detail="API key looks invalid")

    current_user.ai_api_key_encrypted = encrypt_secret(api_key)
    current_user.ai_api_key_masked = _mask_api_key(api_key)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return UserAiKeyStatus(has_key=True, masked_key=current_user.ai_api_key_masked)


@router.delete("/me/ai-key", status_code=204)
def delete_my_ai_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.ai_api_key_encrypted = None
    current_user.ai_api_key_masked = None
    db.add(current_user)
    db.commit()

    return None

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    is_admin = current_user.role in {"admin", "dev"}
    if not is_admin and current_user.id != user_id:
        raise HTTPException(403, "Forbidden")

    return user

@router.post("/", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already exists")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username already exists")
    user = User(
        username=data.username,
        email=data.email,
        phone=data.phone,
        # Public create route must not allow role escalation.
        role="user",
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    is_admin = current_user.role in {"admin", "dev"}
    if not is_admin and current_user.id != user_id:
        raise HTTPException(403, "Forbidden")

    update_data = data.model_dump(exclude_unset=True)

    # Non-admin users cannot change roles.
    if not is_admin and 'role' in update_data:
        update_data.pop('role')

    if 'password' in update_data:
        update_data['password_hash'] = hash_password(update_data.pop('password'))
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    is_admin = current_user.role in {"admin", "dev"}
    if not is_admin and current_user.id != user_id:
        raise HTTPException(403, "Forbidden")

    db.delete(user)
    db.commit()
    return None