from pydantic import BaseModel, Field


class WebhookCreate(BaseModel):
    name: str
    url: str
    color: int = Field(0, ge=0, le=16777215)


class WebhookUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    color: int | None = Field(None, ge=0, le=16777215)
    enabled: bool | None = None


class WebhookOut(BaseModel):
    id: int
    name: str
    url: str
    color: int
    enabled: bool

