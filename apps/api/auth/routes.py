from fastapi import APIRouter, Depends, Request, Response

from .schemas import AuthResponse, MFAChallengeRequest, MFAVerifyRequest
from .service import (
    check_mfa_required,
    get_current_user,
    logout,
    start_mfa_challenge,
    verify_mfa_code,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=AuthResponse)
async def auth_me_endpoint(current_user=Depends(get_current_user)):
    return AuthResponse(user=current_user, authenticated=True)


@router.post("/logout")
async def logout_endpoint(response: Response):
    response.delete_cookie(key="stytch_session", path="/", samesite="lax")
    return await logout()


@router.post("/mfa/check")
async def check_mfa_endpoint(request: Request, current_user=Depends(get_current_user)):
    mfa_required = await check_mfa_required(current_user.user_id, request)
    return {"mfa_required": mfa_required, "user_id": current_user.user_id}


@router.post("/mfa/challenge")
async def start_mfa_challenge_endpoint(request: MFAChallengeRequest):
    return await start_mfa_challenge(request)


@router.post("/mfa/verify")
async def verify_mfa_endpoint(request: MFAVerifyRequest):
    return await verify_mfa_code(request)
