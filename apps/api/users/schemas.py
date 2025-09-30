from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class UserOut(BaseModel):
    id: UUID
    email: str
    name: Optional[str] = None
    stytch_user_id: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

