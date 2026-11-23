from pydantic import BaseModel


class PermissionRule(BaseModel):
    command: str
    roles: list[str] = []
    permissions: list[str] = []


class PermissionRuleUpdate(BaseModel):
    roles: list[str] = []
    permissions: list[str] = []

