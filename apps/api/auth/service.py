import os
import time
import logging
import hashlib
from typing import Dict, Optional

import stytch
from fastapi import Request

from .schemas import User
from .exceptions import (
    AuthenticationError,
    InvalidSessionError,
    SessionNotFoundError,
    StytchError,
)

logger = logging.getLogger(__name__)

STYTCH_PROJECT_ID = os.getenv("STYTCH_PROJECT_ID")
STYTCH_SECRET = os.getenv("STYTCH_SECRET")

if not STYTCH_PROJECT_ID or not STYTCH_SECRET:
    raise ValueError("Missing required Stytch environment variables: STYTCH_PROJECT_ID and STYTCH_SECRET")

stytch_client = stytch.Client(
    project_id=STYTCH_PROJECT_ID,
    secret=STYTCH_SECRET,
)

session_cache: Dict[str, Dict] = {}


def get_session_fingerprint(request: Request) -> str:
    user_agent = request.headers.get("user-agent", "")
    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = request.client.host if request.client else ""
    fingerprint_data = f"{client_ip}:{forwarded_for}:{user_agent}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()


async def get_current_user(request: Request) -> User:
    logger.info("🔐 AUTH: Starting user authentication check")
    session_token = request.cookies.get("stytch_session")
    if not session_token:
        logger.warning("❌ AUTH: No Stytch session cookie found in request")
        raise SessionNotFoundError("No session cookie")

    logger.info(f"🍪 AUTH: Found Stytch session cookie: {session_token[:10]}...")

    try:
        fingerprint = get_session_fingerprint(request)
        logger.info(f"🔍 AUTH: Generated session fingerprint: {fingerprint[:8]}...")

        new_session_token = await rotate_session_if_needed(session_token)
        if new_session_token:
            logger.info("🔄 AUTH: Session rotated, updating cache")
            old_cache_key = f"{session_token}:{fingerprint}"
            if old_cache_key in session_cache:
                del session_cache[old_cache_key]
            session_token = new_session_token

        session_data = await validate_session_with_cache(session_token, fingerprint)
        if not session_data:
            logger.warning("❌ AUTH: Session validation failed")
            raise InvalidSessionError("Invalid or expired session")

        if session_data.get("fingerprint") != fingerprint:
            logger.warning("❌ AUTH: Session fingerprint mismatch - possible session hijacking")
            raise InvalidSessionError("Session security violation")

        logger.info(f"✅ AUTH: Successfully authenticated user: {session_data['user_id']}")
        logger.info(f"👤 AUTH: User email: {session_data['email']}")

        return User(
            user_id=session_data["user_id"],
            email=session_data["email"],
            name=session_data["name"],
        )

    except AuthenticationError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"Authentication error for user: {exc}", exc_info=True)
        raise StytchError("Authentication service error")


async def validate_session_with_cache(session_token: str, fingerprint: str) -> Optional[Dict]:
    cache_key = f"{session_token}:{fingerprint}"

    if cache_key in session_cache:
        cached_session = session_cache[cache_key]
        cache_age = time.time() - cached_session["timestamp"]

        if cache_age < 300:
            return cached_session["data"]

        if cache_age > 900:
            logger.info("🔄 AUTH: Session rotation required")
            del session_cache[cache_key]

    try:
        resp = stytch_client.sessions.authenticate(session_token)
        user_data = resp.session

        if user_data and getattr(user_data, "user_id", None):
            session_data = await _build_session_data(user_data, fingerprint)
            session_cache[cache_key] = {
                "data": session_data,
                "timestamp": time.time(),
            }
            return session_data
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"Session validation error: {exc}")

    return None


async def rotate_session_if_needed(session_token: str) -> Optional[str]:
    try:
        resp = stytch_client.sessions.authenticate(session_token)

        if resp.session and hasattr(resp.session, "started_at"):
            session_age = time.time() - resp.session.started_at.timestamp()
            if session_age > 1800:
                logger.info("🔄 AUTH: Rotating session token")
                rotate_resp = stytch_client.sessions.rotate(session_token)
                return rotate_resp.session_token

    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"Session rotation error: {exc}")

    return None


async def _build_session_data(user_data, fingerprint: str) -> Dict:
    try:
        user_resp = stytch_client.users.get(user_data.user_id)
        user_info = user_resp

        email = user_info.emails[0].email if getattr(user_info, "emails", None) else f"{user_data.user_id}@stytch.local"
        name = None
        if getattr(user_info, "name", None):
            first = getattr(user_info.name, "first_name", "").strip()
            last = getattr(user_info.name, "last_name", "").strip()
            name = f"{first} {last}".strip() or None

        return {
            "user_id": user_data.user_id,
            "email": email,
            "name": name,
            "fingerprint": fingerprint,
            "last_validated": time.time(),
            "session_id": getattr(user_data, "session_id", None),
        }
    except Exception as exc:  # pragma: no cover - fallback path
        logger.error(f"User details fetch error: {exc}")
        return {
            "user_id": user_data.user_id,
            "email": f"{user_data.user_id}@stytch.local",
            "name": None,
            "fingerprint": fingerprint,
            "last_validated": time.time(),
            "session_id": getattr(user_data, "session_id", None),
        }


async def logout() -> Dict[str, object]:
    return {"success": True, "message": "Logged out successfully"}


async def check_mfa_required(user_id: str, request: Request) -> bool:
    try:
        user_resp = stytch_client.users.get(user_id)
        user = user_resp

        has_totp = any(getattr(factor, "type", None) == "totp" for factor in getattr(user, "totps", []) or [])
        has_sms = any(getattr(phone, "type", None) == "sms" for phone in getattr(user, "phone_numbers", []) or [])

        if not has_totp and not has_sms:
            return False

        _ = get_session_fingerprint(request)  # placeholder for adaptive checks
        return True
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"MFA check error: {exc}")
        return False


async def start_mfa_challenge(request) -> Dict[str, object]:
    try:
        if request.challenge_type == "sms":
            stytch_client.otps.sms.send(
                phone_number=request.user_id,
                expiration_minutes=10,
            )
            return {"success": True, "message": "SMS code sent"}

        if request.challenge_type == "totp":
            return {"success": True, "message": "Enter code from authenticator app"}
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"MFA challenge error: {exc}")
        return {"success": False, "message": "Failed to send challenge"}

    return {"success": False, "message": "Invalid challenge type"}


async def verify_mfa_code(request) -> Dict[str, object]:
    try:
        if request.challenge_type == "sms":
            stytch_client.otps.sms.authenticate(
                code=request.code,
                phone_number=request.user_id,
            )
            return {"success": True, "message": "MFA verified"}

        if request.challenge_type == "totp":
            stytch_client.totps.authenticate(
                code=request.code,
                user_id=request.user_id,
            )
            return {"success": True, "message": "MFA verified"}
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"MFA verification error: {exc}")
        return {"success": False, "message": "Invalid code"}

    return {"success": False, "message": "Invalid challenge type"}
