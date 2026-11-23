"""Password hashing, JWT, and API-key helpers."""
from __future__ import annotations

import hashlib
import hmac
import time

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from api.app.config import Settings, get_settings

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def create_access_token(
    settings: Settings, username: str, role: str
) -> tuple[str, int]:
    now = int(time.time())
    expires_in = settings.token_expires_minutes * 60
    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + expires_in,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_in


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError:
        raise credentials_exception
    username = payload.get("sub")
    role = payload.get("role", "user")
    if not username:
        raise credentials_exception
    return {"username": username, "role": role}


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_api_key(raw_key), stored_hash)
