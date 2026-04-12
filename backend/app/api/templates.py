"""Use case template endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.reminder import UseCaseTemplate

router = APIRouter()


class TemplateResponse(BaseModel):
    """Template response model"""
    id: int
    name: str
    description: str | None
    condition: str
    hours_ahead: int
    message_template: str

    class Config:
        from_attributes = True


@router.get("/", response_model=list[TemplateResponse])
def list_templates(
    db: Session = Depends(get_db)
):
    """
    List all active use case templates.

    This endpoint is public (no authentication required) as templates
    are used during the initial configuration before users link their
    Telegram account.

    Returns all active templates ordered by name for frontend dropdown display.
    """
    # Query all active templates
    templates = (
        db.query(UseCaseTemplate)
        .filter(UseCaseTemplate.is_active == True)
        .order_by(UseCaseTemplate.name)
        .all()
    )

    return [
        TemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            condition=template.condition,
            hours_ahead=template.hours_ahead,
            message_template=template.message_template
        )
        for template in templates
    ]
