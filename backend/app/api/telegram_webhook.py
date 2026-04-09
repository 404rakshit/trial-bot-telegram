"""Telegram webhook handler"""
from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings

router = APIRouter()


@router.post("/telegram")
async def telegram_webhook(request: Request):
    """
    Receive Telegram bot updates via webhook.

    TODO: Implement in Phase 3
    - Validate Telegram signature
    - Handle /start command
    - Handle /link <OTP> command
    - Handle /list command
    """
    # Verify webhook is from Telegram (security)
    # For now, just accept all requests

    data = await request.json()

    # TODO: Process Telegram update
    # - Extract command and chat_id
    # - Route to appropriate handler

    return {"status": "ok"}
