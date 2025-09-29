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

class MFAChallengeRequest(BaseModel):
    user_id: str
    challenge_type: str  # "sms", "totp"

class MFAVerifyRequest(BaseModel):
    user_id: str
    code: str
    challenge_type: str

# Cookie-based authentication dependency
async def get_current_user(request: Request) -> User:
    """Validate Stytch session with caching and fingerprinting"""
    logger.info("🔐 AUTH: Starting user authentication check")
    
    # Look for Stytch session cookie directly
    session_token = request.cookies.get("stytch_session")
    if not session_token:
        logger.warning("❌ AUTH: No Stytch session cookie found in request")
        raise SessionNotFoundError("No session cookie")

    logger.info(f"🍪 AUTH: Found Stytch session cookie: {session_token[:10]}...")

    try:
        # Generate session fingerprint for security
        fingerprint = get_session_fingerprint(request)
        logger.info(f"🔍 AUTH: Generated session fingerprint: {fingerprint[:8]}...")

        # Check for session rotation
        new_session_token = await rotate_session_if_needed(session_token)
        if new_session_token:
            logger.info("🔄 AUTH: Session rotated, updating cache")
            # Clear old cache entries
            old_cache_key = f"{session_token}:{fingerprint}"
            if old_cache_key in session_cache:
                del session_cache[old_cache_key]
            session_token = new_session_token

        # Validate session with caching
        session_data = await validate_session_with_cache(session_token, fingerprint)
        
        if not session_data:
            logger.warning("❌ AUTH: Session validation failed")
            raise InvalidSessionError("Invalid or expired session")

        # Check fingerprint match for security
        if session_data.get("fingerprint") != fingerprint:
            logger.warning("❌ AUTH: Session fingerprint mismatch - possible session hijacking")
            raise InvalidSessionError("Session security violation")

        logger.info(f"✅ AUTH: Successfully authenticated user: {session_data['user_id']}")
        logger.info(f"👤 AUTH: User email: {session_data['email']}")

        return User(
            user_id=session_data["user_id"],
            email=session_data["email"],
            name=session_data["name"]
        )

    except AuthenticationError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Log the actual error for debugging but don't expose it to client
        logger.error(f"Authentication error for user: {str(e)}", exc_info=True)
        raise StytchError("Authentication service error")

# Session rotation and security features

# In-memory session cache for performance
session_cache: Dict[str, Dict] = {}

def get_session_fingerprint(request: Request) -> str:
    """Generate session fingerprint from request headers"""
    user_agent = request.headers.get("user-agent", "")
    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = request.client.host if request.client else ""
    
    fingerprint_data = f"{client_ip}:{forwarded_for}:{user_agent}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()

async def validate_session_with_cache(session_token: str, fingerprint: str) -> Optional[Dict]:
    """Validate session with caching and rotation for performance"""
    cache_key = f"{session_token}:{fingerprint}"
    
    # Check cache first
    if cache_key in session_cache:
        cached_session = session_cache[cache_key]
        cache_age = time.time() - cached_session["timestamp"]
        
        # Return cached data if less than 5 minutes old
        if cache_age < 300:
            return cached_session["data"]
        
        # Check if session needs rotation (15 minutes)
        if cache_age > 900:  # 15 minutes
            logger.info("🔄 AUTH: Session rotation required")
            # Clear cache to force fresh validation
            del session_cache[cache_key]
    
    # Validate with Stytch
    try:
        resp = stytch_client.sessions.authenticate(session_token)
        user_data = resp.session
        
        if user_data and hasattr(user_data, 'user_id') and user_data.user_id:
            # Get user details
            try:
                user_resp = stytch_client.users.get(user_data.user_id)
                user_info = user_resp
                
                # Extract email and name safely
                email = None
                name = None
                
                if hasattr(user_info, 'emails') and user_info.emails:
                    email = user_info.emails[0].email
                else:
                    email = f"{user_data.user_id}@stytch.local"
                
                if hasattr(user_info, 'name') and user_info.name:
                    if hasattr(user_info.name, 'first_name') and hasattr(user_info.name, 'last_name'):
                        name = f"{user_info.name.first_name} {user_info.name.last_name}".strip()
                
                session_data = {
                    "user_id": user_data.user_id,
                    "email": email,
                    "name": name,
                    "fingerprint": fingerprint,
                    "last_validated": time.time(),
                    "session_id": getattr(user_data, 'session_id', None)
                }
            except Exception as e:
                logger.error(f"User details fetch error: {str(e)}")
                # Fallback to basic session data
                session_data = {
                    "user_id": user_data.user_id,
                    "email": f"{user_data.user_id}@stytch.local",
                    "name": None,
                    "fingerprint": fingerprint,
                    "last_validated": time.time(),
                    "session_id": getattr(user_data, 'session_id', None)
                }
            
            # Cache the result
            session_cache[cache_key] = {
                "data": session_data,
                "timestamp": time.time()
            }
            
            return session_data
    except Exception as e:
        logger.error(f"Session validation error: {str(e)}")
    
    return None

async def rotate_session_if_needed(session_token: str) -> Optional[str]:
    """Rotate session token if needed"""
    try:
        # Check session age with Stytch
        resp = stytch_client.sessions.authenticate(session_token)
        
        if resp.session:
            # Check if session is older than 30 minutes using started_at
            if hasattr(resp.session, 'started_at'):
                session_age = time.time() - resp.session.started_at.timestamp()
                if session_age > 1800:  # 30 minutes
                    logger.info("🔄 AUTH: Rotating session token")
                    rotate_resp = stytch_client.sessions.rotate(session_token)
                    return rotate_resp.session_token
        
    except Exception as e:
        logger.error(f"Session rotation error: {str(e)}")
    
    return None

def create_auth_response(current_user: User):
    """Create auth response from user object"""
    return AuthResponse(
        user=current_user,
        authenticated=True
    )

async def logout():
    """Get logout response data"""
    return {"success": True, "message": "Logged out successfully"}

# MFA functions
async def check_mfa_required(user_id: str, request: Request) -> bool:
    """Check if MFA is required for this user/request"""
    # Check if user has MFA enabled
    try:
        user_resp = stytch_client.users.get(user_id)
        user = user_resp
        
        # Check if user has MFA factors configured
        has_totp = False
        has_sms = False
        
        if hasattr(user, 'totps') and user.totps:
            has_totp = any(hasattr(factor, 'type') and factor.type == "totp" for factor in user.totps)
        
        if hasattr(user, 'phone_numbers') and user.phone_numbers:
            has_sms = any(hasattr(phone, 'type') and phone.type == "sms" for phone in user.phone_numbers)
        
        if not has_totp and not has_sms:
            return False
            
        # Check for adaptive triggers (new device, high-value action, etc.)
        fingerprint = get_session_fingerprint(request)
        
        # For now, require MFA for new devices (simplified logic)
        # In production, you'd check against a device registry
        return True
        
    except Exception as e:
        logger.error(f"MFA check error: {str(e)}")
        return False

async def start_mfa_challenge(request: MFAChallengeRequest) -> dict:
    """Start MFA challenge"""
    try:
        if request.challenge_type == "sms":
            # Send SMS code
            resp = stytch_client.otps.sms.send(
                phone_number=request.user_id,  # In production, get from user profile
                expiration_minutes=10
            )
            return {"success": True, "message": "SMS code sent"}
            
        elif request.challenge_type == "totp":
            # For TOTP, user needs to generate code from their authenticator app
            return {"success": True, "message": "Enter code from authenticator app"}
            
    except Exception as e:
        logger.error(f"MFA challenge error: {str(e)}")
        return {"success": False, "message": "Failed to send challenge"}
    
    return {"success": False, "message": "Invalid challenge type"}

async def verify_mfa_code(request: MFAVerifyRequest) -> dict:
    """Verify MFA code"""
    try:
        if request.challenge_type == "sms":
            resp = stytch_client.otps.sms.authenticate(
                code=request.code,
                phone_number=request.user_id  # In production, get from user profile
            )
            return {"success": True, "message": "MFA verified"}
            
        elif request.challenge_type == "totp":
            resp = stytch_client.totps.authenticate(
                code=request.code,
                user_id=request.user_id
            )
            return {"success": True, "message": "MFA verified"}
            
    except Exception as e:
        logger.error(f"MFA verification error: {str(e)}")
        return {"success": False, "message": "Invalid code"}
    
    return {"success": False, "message": "Invalid challenge type"}
