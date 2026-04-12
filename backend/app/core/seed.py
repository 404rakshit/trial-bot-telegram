"""Database seeding utilities"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.reminder import UseCaseTemplate


WEATHER_TEMPLATES = [
    {
        "name": "Rain Alert",
        "description": "Get notified when rain is expected in the next 6 hours",
        "condition": "rain",
        "hours_ahead": 6,
        "message_template": "🌧️ Rain expected in 6 hours! Don't forget your umbrella."
    },
    {
        "name": "Snow Alert",
        "description": "Get notified when snow is expected in the next 12 hours",
        "condition": "snow",
        "hours_ahead": 12,
        "message_template": "❄️ Snow expected in 12 hours! Prepare for winter weather."
    },
    {
        "name": "Hot Day Tomorrow",
        "description": "Get notified if tomorrow will be hot (24 hours ahead)",
        "condition": "hot",
        "hours_ahead": 24,
        "message_template": "🌡️ Hot weather tomorrow! Stay hydrated and use sunscreen."
    },
    {
        "name": "Cold Night Tonight",
        "description": "Get notified if tonight will be cold (12 hours ahead)",
        "condition": "cold",
        "hours_ahead": 12,
        "message_template": "🥶 Cold night ahead! Dress warmly and bundle up."
    },
    {
        "name": "Clear Weekend",
        "description": "Get notified if the weekend will have clear skies (72 hours ahead)",
        "condition": "clear",
        "hours_ahead": 72,
        "message_template": "☀️ Clear skies this weekend! Perfect for outdoor activities."
    }
]


async def seed_templates(db: AsyncSession) -> int:
    """
    Seed UseCaseTemplate table with default weather templates.

    This function is idempotent - it will only create templates that don't exist yet.
    Templates are matched by name to avoid duplicates.

    Args:
        db: AsyncSession database session

    Returns:
        Number of new templates created
    """
    created_count = 0

    for template_data in WEATHER_TEMPLATES:
        # Check if template with this name already exists
        result = await db.execute(
            select(UseCaseTemplate).where(UseCaseTemplate.name == template_data["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Template already exists, skip
            continue

        # Create new template
        template = UseCaseTemplate(
            name=template_data["name"],
            description=template_data["description"],
            condition=template_data["condition"],
            hours_ahead=template_data["hours_ahead"],
            message_template=template_data["message_template"],
            is_active=True
        )

        db.add(template)
        created_count += 1

    # Commit all new templates
    if created_count > 0:
        await db.commit()

    return created_count
