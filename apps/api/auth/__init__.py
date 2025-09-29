from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import logging
import time
import hashlib
from typing import Optional, Dict
import stytch

from .schemas import User, AuthResponse, MFAChallengeRequest, MFAVerifyRequest
from .service import (
    get_current_user,
    logout,
    check_mfa_required,
    start_mfa_challenge,
    verify_mfa_code,
)
from .exceptions import (
    AuthenticationError,
    SessionNotFoundError,
    InvalidSessionError,
    StytchError,
)
from .routes import router

__all__ = [
    "User",
    "AuthResponse",
    "MFAChallengeRequest",
    "MFAVerifyRequest",
    "get_current_user",
    "logout",
    "check_mfa_required",
    "start_mfa_challenge",
    "verify_mfa_code",
    "AuthenticationError",
    "SessionNotFoundError",
    "InvalidSessionError",
    "StytchError",
    "router",
]
