"""OTP generation endpoint"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import secrets
from app.core.redis_client import get_redis
from app.core.config import settings

router = APIRouter()


class OTPRequest(BaseModel):
    """Request body for OTP generation"""
    session_id: str  # Frontend-generated unique session ID


class OTPResponse(BaseModel):
    """OTP generation response"""
    otp: str
    expires_in: int  # seconds


@router.post("/generate", response_model=OTPResponse)
async def generate_otp(request: OTPRequest):
    """
    Generate a 6-digit OTP and store in Redis with 10-minute TTL.

    This prevents spam by requiring the user to complete the Telegram linking
    within 10 minutes of requesting the OTP.
    """
    # Generate 6-digit OTP
    otp = f"{secrets.randbelow(1000000):06d}"

    # Store in Redis: key = "otp:{otp}", value = session_id
    redis = get_redis()
    key = f"otp:{otp}"

    # Check if OTP already exists (collision, very rare)
    if await redis.exists(key):
        # Try one more time
        otp = f"{secrets.randbelow(1000000):06d}"
        key = f"otp:{otp}"

    # Store OTP with session_id
    await redis.setex(
        key,
        settings.REDIS_OTP_TTL,
        request.session_id
    )

    return OTPResponse(
        otp=otp,
        expires_in=settings.REDIS_OTP_TTL
    )
