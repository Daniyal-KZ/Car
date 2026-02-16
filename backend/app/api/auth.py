from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db
from app.models import User
from app.core.security import verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", status_code=200)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token({"user_id": user.id})

    response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    samesite="lax",  # для localhost
    secure=False,    # для localhost
    max_age=60*60*24*7,
    path="/"
)

    # Return token in response body as well so SPA can store/use it in Authorization header
    return {"ok": True, "access_token": access_token}


def get_current_user(
    access_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    token = None

    # Prefer Authorization header if provided
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    else:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
