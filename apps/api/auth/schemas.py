from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None


class AuthResponse(BaseModel):
    user: User
    authenticated: bool


class MFAChallengeRequest(BaseModel):
    user_id: str
    challenge_type: str  # "sms", "totp"


class MFAVerifyRequest(BaseModel):
    user_id: str
    code: str
    challenge_type: str
