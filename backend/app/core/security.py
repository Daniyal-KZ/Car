import os
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet, InvalidToken

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хэширование пароля
def hash_password(password: str) -> str:
    if len(password.encode('utf-8')) > 72:
        password_bytes = password.encode('utf-8')[:72]
        password = password_bytes.decode('utf-8', 'ignore')
    return pwd_context.hash(password)

# Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Создание JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Декодирование JWT
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            return None
        return payload
    except JWTError:
        return None


def _build_ai_key_cipher() -> Fernet:
    # Keep deterministic encryption key per deployment.
    # Explicit AI_KEY_ENCRYPTION_KEY has priority.
    source = os.getenv("AI_KEY_ENCRYPTION_KEY") or f"fallback::{SECRET_KEY}"
    key = base64.urlsafe_b64encode(hashlib.sha256(source.encode("utf-8")).digest())
    return Fernet(key)


def encrypt_secret(secret: str) -> str:
    cipher = _build_ai_key_cipher()
    return cipher.encrypt(secret.encode("utf-8")).decode("utf-8")


def decrypt_secret(secret_encrypted: str) -> Optional[str]:
    cipher = _build_ai_key_cipher()
    try:
        return cipher.decrypt(secret_encrypted.encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        return None
