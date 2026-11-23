"""Pydantic request/response models."""
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeResponse(BaseModel):
    username: str
    role: str


class WarnOut(BaseModel):
    id: int
    user_id: int
    server_id: int
    moderator_id: int
    reason: str
    created_at: str
