from pydantic import BaseModel


class WarnOut(BaseModel):
    id: int
    user_id: int
    server_id: int
    moderator_id: int
    reason: str
    created_at: str

