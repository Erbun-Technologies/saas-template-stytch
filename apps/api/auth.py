from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import logging
from typing import Optional
import stytch

# Set up logging
logger = logging.getLogger(__name__)

# Stytch configuration
STYTCH_PROJECT_ID = os.getenv("STYTCH_PROJECT_ID")
STYTCH_SECRET = os.getenv("STYTCH_SECRET")

if not STYTCH_PROJECT_ID or not STYTCH_SECRET:
    raise ValueError("Missing required Stytch environment variables: STYTCH_PROJECT_ID and STYTCH_SECRET")

# Initialize Stytch client
stytch_client = stytch.Client(
    project_id=STYTCH_PROJECT_ID,
    secret=STYTCH_SECRET,
)

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Custom exceptions
class AuthenticationError(Exception):
    """Base authentication error"""
    pass

class SessionNotFoundError(AuthenticationError):
    """Session not found in request"""
    pass

class InvalidSessionError(AuthenticationError):
    """Session validation failed"""
    pass

class StytchError(AuthenticationError):
    """Stytch API error"""
    pass

# Pydantic models
class User(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None

class AuthResponse(BaseModel):
    user: User
    authenticated: bool

class SessionEstablishRequest(BaseModel):
    session_token: str

class SessionEstablishResponse(BaseModel):
    success: bool
    user: User

# Cookie-based authentication dependency
async def get_current_user(request: Request) -> User:
    """Validate session cookie and return current user"""
    session_token = request.cookies.get("stytch_session")
    if not session_token:
        logger.warning("Authentication attempt without session cookie")
        raise SessionNotFoundError("No session cookie")

    try:
        logger.debug(f"Validating session for token: {session_token[:10]}...")

        # Validate session with Stytch
        resp = stytch_client.sessions.authenticate(session_token)

        # Extract user information from the session object
        user_data = resp.session
        if user_data is None:
            logger.warning("Stytch returned None session")
            raise InvalidSessionError("Session not found")

        if not hasattr(user_data, 'user_id') or not user_data.user_id:
            logger.warning("Session missing user_id")
            raise InvalidSessionError("Missing user ID in session")

        # For session authentication, session contains user_id but not email/name
        # In production, fetch user profile from database or Stytch user API
        primary_email = f"{user_data.user_id}@stytch.local"
        name = None  # Not available in session object

        logger.info(f"Successfully authenticated user: {user_data.user_id}")

        return User(
            user_id=user_data.user_id,
            email=primary_email,
            name=name
        )

    except AuthenticationError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Log the actual error for debugging but don't expose it to client
        logger.error(f"Authentication error for user: {str(e)}", exc_info=True)
        raise StytchError("Authentication service error")

# Auth endpoints
def get_session_cookies(session_token: str):
    """Get cookie data for session establishment"""
    csrf_token = str(uuid.uuid4())
    return {
        "session_cookie": {
            "key": "stytch_session",
            "value": session_token,
            "httponly": True,
            "secure": IS_PRODUCTION,
            "samesite": "lax",
            "max_age": 60 * 60
        },
        "csrf_cookie": {
            "key": "csrf_token",
            "value": csrf_token,
            "httponly": False,
            "secure": IS_PRODUCTION,
            "samesite": "lax",
            "max_age": 60 * 60
        }
    }

async def establish_session(request: SessionEstablishRequest):
    """Establish a session by validating Stytch session token and returning user data"""
    try:
        logger.debug(f"Establishing session for token: {request.session_token[:10]}...")

        # Validate the session token with Stytch
        resp = stytch_client.sessions.authenticate(request.session_token)

        user_data = resp.session
        if user_data is None or not hasattr(user_data, 'user_id') or not user_data.user_id:
            logger.warning("Invalid session token provided")
            raise InvalidSessionError("Invalid session token")

        # Create user object
        primary_email = f"{user_data.user_id}@stytch.local"
        user = User(
            user_id=user_data.user_id,
            email=primary_email,
            name=None
        )

        logger.info(f"Successfully established session for user: {user_data.user_id}")
        return SessionEstablishResponse(success=True, user=user)

    except AuthenticationError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logger.error(f"Session establishment error: {str(e)}", exc_info=True)
        raise StytchError("Session establishment failed")

def create_auth_response(current_user: User):
    """Create auth response from user object"""
    return AuthResponse(
        user=current_user,
        authenticated=True
    )

async def logout():
    """Get logout response data"""
    return {"success": True, "message": "Logged out successfully"}
