from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette_csrf import CSRFMiddleware
from pydantic import BaseModel
from datetime import datetime
import os
import time
import logging
from collections import defaultdict

# Set up logging
logger = logging.getLogger(__name__)

# Simple rate limiting for auth endpoints
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # requests
RATE_LIMIT_WINDOW = 60    # seconds

def check_rate_limit(client_ip: str, endpoint: str) -> bool:
    """Check if client has exceeded rate limit"""
    key = f"{client_ip}:{endpoint}"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Clean old requests
    rate_limit_store[key] = [req_time for req_time in rate_limit_store[key] if req_time > window_start]

    # Check if under limit
    if len(rate_limit_store[key]) >= RATE_LIMIT_REQUESTS:
        return False

    # Add current request
    rate_limit_store[key].append(now)
    return True

from auth import router as auth_router
from auth.exceptions import (
    AuthenticationError,
    InvalidSessionError,
    SessionNotFoundError,
    StytchError,
)

app = FastAPI(
    title="SaaS Template API",
    description="Backend API for SaaS Template",
    version="0.1.0",
)

app.include_router(auth_router)

# CSRF protection middleware (must be before CORS)
app.add_middleware(
    CSRFMiddleware,
    secret=os.getenv("CSRF_SECRET_KEY", "dev-secret-key"),
    cookie_secure=os.getenv("ENVIRONMENT", "development") == "production",
    cookie_httponly=True,
)

# CORS configuration for SPA
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Alternative localhost
        "http://frontend:5173",   # Docker service name
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception handlers for custom auth errors
@app.exception_handler(SessionNotFoundError)
async def session_not_found_handler(request, exc: SessionNotFoundError):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )

@app.exception_handler(InvalidSessionError)
async def invalid_session_handler(request, exc: InvalidSessionError):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session"
    )

@app.exception_handler(StytchError)
async def stytch_error_handler(request, exc: StytchError):
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Authentication service temporarily unavailable"
    )

@app.exception_handler(AuthenticationError)
async def auth_error_handler(request, exc: AuthenticationError):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication failed"
    )

# Rate limiting middleware for auth endpoints
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to auth endpoints"""
    if request.url.path.startswith("/auth/"):
        client_ip = request.client.host if request.client else "unknown"
        if not check_rate_limit(client_ip, request.url.path):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
    response = await call_next(request)
    return response


# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


# Public endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0"
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SaaS Template API is running"}

@app.get("/csrf-token")
async def get_csrf_token(request: Request):
    """Ensure CSRF cookie is set and return the token for double-submit protection."""
    logger.info("🎯 ENDPOINT: /csrf-token GET request received")
    csrf_token = request.cookies.get("csrftoken")
    return {"message": "CSRF token set in cookie", "token": csrf_token}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
