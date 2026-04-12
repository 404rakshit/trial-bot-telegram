"""OTP generation endpoint"""
from fastapi import APIRouter
from pydantic import BaseModel
import secrets
from app.core.session_store import save_otp, get_otp
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
def generate_otp(request: OTPRequest):
    """
    Generate a 6-digit OTP and store in memory with 10-minute TTL.

    This prevents spam by requiring the user to complete the Telegram linking
    within 10 minutes of requesting the OTP.
    """
    # Generate 6-digit OTP
    otp = f"{secrets.randbelow(1000000):06d}"

    # Check if OTP already exists (collision, very rare)
    if get_otp(otp) is not None:
        # Try one more time
        otp = f"{secrets.randbelow(1000000):06d}"

    # Store OTP with session_id
    save_otp(otp, request.session_id, settings.OTP_TTL)

    return OTPResponse(
        otp=otp,
        expires_in=settings.OTP_TTL
    )
