"""Reminder management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.reminder import Reminder, UseCaseTemplate

router = APIRouter()


class ReminderCreate(BaseModel):
    """Create reminder request"""
    condition: str = Field(..., min_length=1, max_length=50, description="Weather condition to monitor (e.g., 'rain', 'snow')")
    hours_ahead: int = Field(..., ge=1, le=168, description="Hours ahead to check (1-168, i.e., up to 7 days)")
    custom_message: Optional[str] = Field(None, max_length=500, description="Optional custom alert message")
    template_id: Optional[int] = Field(None, description="Optional template ID to use")


class ReminderResponse(BaseModel):
    """Reminder response"""
    id: int
    user_id: int
    template_id: Optional[int]
    condition: str
    hours_ahead: int
    custom_message: Optional[str]
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=list[ReminderResponse])
def list_reminders(
    limit: int = Query(50, ge=1, le=100, description="Number of reminders to return (max 100)"),
    offset: int = Query(0, ge=0, description="Number of reminders to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List active reminders for the authenticated user.

    - **limit**: Number of reminders to return (default 50, max 100)
    - **offset**: Number of reminders to skip for pagination (default 0)
    - Returns only active reminders (is_active=True)
    - Ordered by created_at descending (newest first)
    """
    # Query active reminders for current user with pagination
    reminders = (
        db.query(Reminder)
        .filter(Reminder.user_id == current_user.id)
        .filter(Reminder.is_active == True)
        .order_by(Reminder.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    # Convert datetime to ISO string for JSON serialization
    response = []
    for reminder in reminders:
        response.append(ReminderResponse(
            id=reminder.id,
            user_id=reminder.user_id,
            template_id=reminder.template_id,
            condition=reminder.condition,
            hours_ahead=reminder.hours_ahead,
            custom_message=reminder.custom_message,
            is_active=reminder.is_active,
            created_at=reminder.created_at.isoformat()
        ))

    return response


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminder(
    reminder: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new weather reminder for the authenticated user.

    - **condition**: Weather condition to monitor (e.g., 'rain', 'snow', 'clear')
    - **hours_ahead**: How many hours ahead to check (1-168)
    - **custom_message**: Optional custom alert message
    - **template_id**: Optional template to base reminder on
    """
    # If template_id is provided, validate it exists
    if reminder.template_id is not None:
        template = (
            db.query(UseCaseTemplate)
            .filter(UseCaseTemplate.id == reminder.template_id)
            .filter(UseCaseTemplate.is_active == True)
            .first()
        )

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template with id {reminder.template_id} not found"
            )

    # Create new reminder
    new_reminder = Reminder(
        user_id=current_user.id,
        template_id=reminder.template_id,
        condition=reminder.condition.lower().strip(),  # Normalize condition
        hours_ahead=reminder.hours_ahead,
        custom_message=reminder.custom_message,
        is_active=True
    )

    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)

    return ReminderResponse(
        id=new_reminder.id,
        user_id=new_reminder.user_id,
        template_id=new_reminder.template_id,
        condition=new_reminder.condition,
        hours_ahead=new_reminder.hours_ahead,
        custom_message=new_reminder.custom_message,
        is_active=new_reminder.is_active,
        created_at=new_reminder.created_at.isoformat()
    )


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a reminder (sets is_active=False).

    - **reminder_id**: ID of the reminder to delete
    - User can only delete their own reminders
    - Returns 404 if reminder not found or doesn't belong to user
    - Uses soft delete to preserve audit history
    """
    # Query reminder and verify ownership
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id)
        .filter(Reminder.user_id == current_user.id)
        .first()
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reminder with id {reminder_id} not found or does not belong to you"
        )

    # Soft delete: set is_active to False
    reminder.is_active = False
    db.commit()

    # 204 No Content - successful deletion with no response body
    return None
