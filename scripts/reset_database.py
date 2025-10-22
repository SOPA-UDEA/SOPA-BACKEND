#!/usr/bin/env python3
"""
Reset Database Script
Clears all data from the database to prepare for fresh seeding
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import database


async def reset_database():
    """Clear all data from all tables in the correct order (respecting foreign key constraints)"""
    try:
        print("🗑️ Resetting database...")

        # Connect to database
        await database.connect()

        # Delete in reverse dependency order to avoid foreign key constraint issues
        print("📋 Deleting group data...")
        await database.group.delete_many()

        print("📋 Deleting subject data...")
        await database.subject.delete_many()

        print("📋 Deleting pensum data...")
        await database.pensum.delete_many()

        print("📋 Deleting academic_program data...")
        await database.academic_program.delete_many()

        print("📋 Deleting classroom data...")
        await database.classroom.delete_many()

        print("📋 Deleting professor data...")
        await database.professor.delete_many()

        print("📋 Deleting academic_schedule data...")
        await database.academic_schedule.delete_many()

        print("📋 Deleting faculty data...")
        await database.faculty.delete_many()

        print("📋 Deleting department data...")
        await database.department.delete_many()

        print("📋 Deleting modality data...")
        await database.modality.delete_many()

        print("✅ Database reset completed successfully!")

    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        sys.exit(1)

    finally:
        # Ensure database is disconnected
        if database.is_connected():
            await database.disconnect()


async def main():
    """Entry point for the reset script"""
    await reset_database()


if __name__ == "__main__":
    asyncio.run(main())
