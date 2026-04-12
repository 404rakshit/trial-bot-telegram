"""Standalone database seeding script

Run this script to seed the database with initial data:
    python seed_db.py

This script is idempotent and can be run multiple times safely.
"""
import asyncio
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import AsyncSessionLocal
from app.core.seed import seed_templates


async def main():
    """Main seeding function"""
    print("Starting database seeding...")

    async with AsyncSessionLocal() as db:
        try:
            # Seed templates
            template_count = await seed_templates(db)
            print(f"✓ Created {template_count} new use case templates")

            if template_count == 0:
                print("ℹ All templates already exist (idempotent operation)")

            print("Database seeding completed successfully!")

        except Exception as e:
            print(f"✗ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
