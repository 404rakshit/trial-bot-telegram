"""API routes"""
from fastapi import APIRouter
from app.api import otp, reminders, telegram_webhook, templates

api_router = APIRouter()

# Include route modules
api_router.include_router(otp.router, prefix="/otp", tags=["OTP"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(telegram_webhook.router, prefix="/webhook", tags=["Webhooks"])
