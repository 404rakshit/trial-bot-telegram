"""
Seed database with default weather templates

Run this after starting the server for the first time:
    python seed_templates.py
"""
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.core.database import SessionLocal, init_db
from app.models.reminder import UseCaseTemplate


def seed_templates():
    """Create default weather alert templates"""
    print("🌱 Seeding database with default templates...")

    # Initialize database (creates tables if needed)
    init_db()

    db = SessionLocal()

    try:
        # Check if templates already exist
        existing = db.query(UseCaseTemplate).count()
        if existing > 0:
            print(f"ℹ️  Database already has {existing} templates")
            return

        # Create default templates
        templates = [
            UseCaseTemplate(
                name="Morning Rain Alert",
                description="Get notified if it will rain in the morning",
                condition="rain",
                hours_ahead=6,
                message_template="🌧️ Rain expected in 6 hours! Don't forget your umbrella.",
                is_active=True
            ),
            UseCaseTemplate(
                name="Evening Rain Alert",
                description="Plan your evening around rain",
                condition="rain",
                hours_ahead=12,
                message_template="🌧️ Rain expected in 12 hours. Plan accordingly!",
                is_active=True
            ),
            UseCaseTemplate(
                name="Snow Alert",
                description="Get notified about snow",
                condition="snow",
                hours_ahead=6,
                message_template="❄️ Snow expected in 6 hours! Dress warmly.",
                is_active=True
            ),
            UseCaseTemplate(
                name="Clear Weather",
                description="Get notified when it will be sunny",
                condition="clear",
                hours_ahead=6,
                message_template="☀️ Clear weather expected in 6 hours! Perfect day ahead.",
                is_active=True
            ),
            UseCaseTemplate(
                name="Storm Warning",
                description="Get notified about storms",
                condition="thunderstorm",
                hours_ahead=3,
                message_template="⛈️ Storm expected in 3 hours! Stay safe indoors.",
                is_active=True
            ),
        ]

        # Add all templates
        for template in templates:
            db.add(template)
            print(f"  ✅ Created template: {template.name}")

        db.commit()
        print(f"\n✅ Successfully seeded {len(templates)} templates")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    seed_templates()
