"""Reminder management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_db
from app.models import Reminder

router = APIRouter()


class ReminderCreate(BaseModel):
    """Create reminder request"""
    condition: str
    hours_ahead: int
    custom_message: str | None = None


class ReminderResponse(BaseModel):
    """Reminder response"""
    id: int
    condition: str
    hours_ahead: int
    custom_message: str | None
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/", response_model=list[ReminderResponse])
async def list_reminders(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    List all active reminders for a user.

    TODO: Implement after Phase 3 (need user authentication)
    """
    raise HTTPException(status_code=501, detail="Not implemented yet - Phase 3")


@router.post("/", response_model=ReminderResponse)
async def create_reminder(
    reminder: ReminderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new weather reminder.

    TODO: Implement after Phase 3 (need user authentication)
    """
    raise HTTPException(status_code=501, detail="Not implemented yet - Phase 3")


@router.delete("/{reminder_id}")
async def delete_reminder(
    reminder_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a reminder.

    TODO: Implement after Phase 3 (need user authentication)
    """
    raise HTTPException(status_code=501, detail="Not implemented yet - Phase 3")
