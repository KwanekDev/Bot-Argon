from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeResponse(BaseModel):
    username: str
    role: str


class ApiKeyCreate(BaseModel):
    name: str


class ApiKeyCreated(BaseModel):
    id: int
    name: str
    key: str


class ApiKeyOut(BaseModel):
    id: int
    name: str
    scopes: str
    created_at: str

