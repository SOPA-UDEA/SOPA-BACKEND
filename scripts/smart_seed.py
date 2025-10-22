#!/usr/bin/env python3
"""
Smart Database Seeding Script
Only runs on first deployment to avoid overwriting existing data
"""

import asyncio
import os
import sys
from pathlib import Path
import httpx  # For API calls to cloud database

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import database
import httpx
import os
from prisma import Prisma


async def sync_from_cloud_database():
    """
    Sync data from cloud database via API
    Replace this with your actual cloud database connection
    """
    try:
        print("🌐 Connecting to cloud database...")

        # Example: If you have a REST API endpoint
        # async with httpx.AsyncClient() as client:
        #     response = await client.get("https://your-cloud-api.com/subjects")
        #     cloud_subjects = response.json()
        #
        #     for subject in cloud_subjects:
        #         await database.subject.create(data=subject)

        # Example: If you have another database connection
        # cloud_db_url = "postgresql://user:pass@cloud-host:5432/db"
        # # Use another Prisma client or direct connection

        print("💡 Implement your cloud database sync logic here")
        print("📝 Options:")
        print("   - REST API calls")
        print("   - Direct database connection")
        print("   - GraphQL queries")
        print("   - File import/export")

        return True

    except Exception as e:
        print(f"❌ Error syncing from cloud: {e}")
        return False


class DatabaseSeeder:
    def __init__(self):
        self.seeded_flag_file = "/app/.db_seeded"

    async def is_database_empty(self):
        """Check if database has any data in key tables"""
        try:
            # Check if main tables have data
            subject_count = await database.subject.count()
            pensum_count = await database.pensum.count()

            return subject_count == 0 and pensum_count == 0
        except Exception as e:
            print(f"Error checking database state: {e}")
            return False

    def is_first_deployment(self):
        """Check if this is the first deployment by looking for seed flag"""
        return not os.path.exists(self.seeded_flag_file)

    def mark_as_seeded(self):
        """Create flag file to mark database as seeded"""
        try:
            with open(self.seeded_flag_file, "w") as f:
                f.write("Database seeded successfully")
            print(f"✅ Created seed flag: {self.seeded_flag_file}")
        except Exception as e:
            print(f"❌ Error creating seed flag: {e}")

    async def seed_database(self):
        """Execute database seeding operations from Neon cloud database"""
        try:
            print("🌱 Starting database seeding from Neon cloud database...")

            # Create a connection to Neon database
            neon_database_url = os.getenv("NEON_DATABASE_URL") or os.getenv(
                "CLOUD_DATABASE_URL"
            )

            if not neon_database_url:
                print("❌ NEON_DATABASE_URL not found in environment variables")
                print("💡 Please set NEON_DATABASE_URL or CLOUD_DATABASE_URL")
                return False

            # Create Neon database connection
            print("🌐 Connecting to Neon database...")
            neon_db = Prisma(datasource={"url": neon_database_url})
            await neon_db.connect()

            # Sync all tables from Neon to local Docker database in dependency order
            # First sync tables with no dependencies
            await self.sync_table_data(neon_db, "faculty")
            await self.sync_table_data(neon_db, "department")
            await self.sync_table_data(neon_db, "modality")

            # Then sync tables that depend on the above
            await self.sync_table_data(neon_db, "academic_program")
            await self.sync_table_data(neon_db, "pensum")

            # Then sync other independent tables
            await self.sync_table_data(neon_db, "classroom")
            await self.sync_table_data(neon_db, "professor")
            await self.sync_table_data(neon_db, "academic_schedule")

            # Finally sync subjects using the optimized raw SQL script
            print("📚 Syncing subjects using optimized script...")
            import subprocess

            result = subprocess.run(
                [
                    sys.executable,
                    os.path.join(os.path.dirname(__file__), "sync_subjects.py"),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ Subject sync completed successfully!")
                print(result.stdout.split("\n")[-3:])  # Show last few lines of output
            else:
                print("❌ Subject sync failed!")
                print(result.stderr)

            # Skip complex tables for now (groups depend on many other tables)
            await self.sync_table_data(neon_db, "group")

            await neon_db.disconnect()

            print("✅ Database seeding from Neon completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Error during database seeding from Neon: {e}")
            return False

    async def sync_table_data(self, neon_db, table_name):
        """Sync data from a specific table in Neon to local database"""
        try:
            print(f"📋 Syncing {table_name} data from Neon...")

            # Get data from Neon with related data
            if table_name == "faculty":
                neon_data = await neon_db.faculty.find_many()
                for item in neon_data:
                    # Check by name to avoid duplicates
                    existing = await database.faculty.find_first(
                        where={"name": item.name}
                    )
                    if not existing:
                        data_dict = {"name": item.name}
                        if hasattr(item, "internalKey") and item.internalKey:
                            data_dict["internalKey"] = item.internalKey
                        await database.faculty.create(data=data_dict)

            elif table_name == "department":
                neon_data = await neon_db.department.find_many()
                for item in neon_data:
                    if item.name:  # Only create if name exists
                        existing = await database.department.find_first(
                            where={"name": item.name}
                        )
                        if not existing:
                            data_dict = {"name": item.name}
                            if hasattr(item, "internalKey") and item.internalKey:
                                data_dict["internalKey"] = item.internalKey
                            await database.department.create(data=data_dict)

            elif table_name == "modality":
                neon_data = await neon_db.modality.find_many()
                for item in neon_data:
                    existing = await database.modality.find_first(
                        where={"name": item.name}
                    )
                    if not existing:
                        data_dict = {"name": item.name}
                        if hasattr(item, "IDE") and item.IDE:
                            data_dict["IDE"] = item.IDE
                        await database.modality.create(data=data_dict)

            elif table_name == "academic_program":
                # Get academic programs with their related data
                neon_data = await neon_db.academic_program.find_many(
                    include={"faculty": True, "department": True, "modality": True}
                )
                for item in neon_data:
                    existing = await database.academic_program.find_first(
                        where={"code": item.code}
                    )
                    if not existing:
                        # Find local IDs for foreign keys
                        local_modality = (
                            await database.modality.find_first(
                                where={"name": item.modality.name}
                            )
                            if item.modality
                            else None
                        )
                        local_faculty = (
                            await database.faculty.find_first(
                                where={"name": item.faculty.name}
                            )
                            if item.faculty
                            else None
                        )
                        local_department = (
                            await database.department.find_first(
                                where={"name": item.department.name}
                            )
                            if item.department
                            else None
                        )

                        if local_modality and local_faculty and local_department:
                            await database.academic_program.create(
                                data={
                                    "name": item.name,
                                    "code": item.code,
                                    "modalityAcademic": item.modalityAcademic,
                                    "headquarter": item.headquarter,
                                    "version": item.version,
                                    "modalityId": local_modality.id,
                                    "facultyId": local_faculty.id,
                                    "departmentId": local_department.id,
                                }
                            )
                        else:
                            print(
                                f"⚠️ Skipping academic_program {item.name}: missing foreign key references"
                            )

            elif table_name == "pensum":
                # Get pensum with related academic program data
                neon_data = await neon_db.pensum.find_many(
                    include={"academic_program": True}
                )
                for item in neon_data:
                    if item.academic_program:
                        local_program = await database.academic_program.find_first(
                            where={"code": item.academic_program.code}
                        )
                        if local_program:
                            # Check if pensum already exists for this program and version
                            existing = await database.pensum.find_first(
                                where={
                                    "academicProgramId": local_program.id,
                                    "version": item.version,
                                }
                            )
                            if not existing:
                                await database.pensum.create(
                                    data={
                                        "version": item.version,
                                        "academicProgramId": local_program.id,
                                    }
                                )
                        else:
                            print(
                                f"⚠️ Skipping pensum {item.id}: academic_program {item.academic_program.code} not found locally"
                            )
                    else:
                        print(
                            f"⚠️ Skipping pensum {item.id}: no academic_program relation"
                        )

            elif table_name == "subject":
                # Subjects are handled by the optimized sync_subjects.py script
                print(f"⏭️ Skipping {table_name} (handled by dedicated script)")
                return

            elif table_name == "classroom":
                neon_data = await neon_db.classroom.find_many()
                for item in neon_data:
                    existing = await database.classroom.find_first(
                        where={"location": item.location}
                    )
                    if not existing:
                        data_dict = {"location": item.location}
                        if hasattr(item, "capacity") and item.capacity is not None:
                            data_dict["capacity"] = item.capacity
                        if (
                            hasattr(item, "ownDepartment")
                            and item.ownDepartment is not None
                        ):
                            data_dict["ownDepartment"] = item.ownDepartment
                        if (
                            hasattr(item, "virtualMode")
                            and item.virtualMode is not None
                        ):
                            data_dict["virtualMode"] = item.virtualMode
                        if hasattr(item, "enabled") and item.enabled is not None:
                            data_dict["enabled"] = item.enabled
                        if hasattr(item, "isPointer") and item.isPointer is not None:
                            data_dict["isPointer"] = item.isPointer
                        if hasattr(item, "hasRoom") and item.hasRoom is not None:
                            data_dict["hasRoom"] = item.hasRoom
                        await database.classroom.create(data=data_dict)

            elif table_name == "professor":
                neon_data = await neon_db.professor.find_many()
                for item in neon_data:
                    # Check by identification or name to avoid duplicates
                    existing = None
                    if hasattr(item, "identification") and item.identification:
                        existing = await database.professor.find_first(
                            where={"identification": item.identification}
                        )
                    else:
                        existing = await database.professor.find_first(
                            where={"name": item.name}
                        )

                    if not existing:
                        data_dict = {"name": item.name}
                        if hasattr(item, "identification") and item.identification:
                            data_dict["identification"] = item.identification
                        await database.professor.create(data=data_dict)

            elif table_name == "academic_schedule":
                neon_data = await neon_db.academic_schedule.find_many()
                for item in neon_data:
                    existing = await database.academic_schedule.find_first(
                        where={"semester": item.semester}
                    )
                    if not existing:
                        await database.academic_schedule.create(
                            data={
                                "semester": item.semester,
                            }
                        )

            elif table_name == "group":
                # Groups depend on other tables, so we'll skip for now
                print(f"⏭️ Skipping {table_name} (depends on other tables)")
                return

            print(f"✅ Synced {len(neon_data)} records from {table_name}")

        except Exception as e:
            print(f"❌ Error syncing {table_name}: {e}")
            # Continue with other tables even if one fails

    async def run(self):
        """Main seeding logic with safety checks"""
        try:
            print("🔍 Checking database seeding requirements...")

            # Connect to database
            await database.connect()

            # Check if this is first deployment AND database is empty
            is_first = self.is_first_deployment()
            is_empty = await self.is_database_empty()

            print(f"📊 First deployment: {is_first}")
            print(f"📊 Database empty: {is_empty}")

            if is_first and is_empty:
                print(
                    "🚀 First deployment detected with empty database. Starting seeding..."
                )

                success = await self.seed_database()

                if success:
                    self.mark_as_seeded()
                    print("✅ Database seeding process completed successfully!")
                else:
                    print("❌ Database seeding failed!")
                    sys.exit(1)

            elif not is_first:
                print("⚠️ Seed flag found. Skipping seeding to preserve existing data.")

            elif not is_empty:
                print(
                    "⚠️ Database contains data. Skipping seeding to preserve existing data."
                )

            else:
                print("ℹ️ No seeding required.")

        except Exception as e:
            print(f"❌ Fatal error in seeding process: {e}")
            sys.exit(1)

        finally:
            # Ensure database is disconnected
            if database.is_connected():
                await database.disconnect()


async def main():
    """Entry point for the seeding script"""
    seeder = DatabaseSeeder()
    await seeder.run()


if __name__ == "__main__":
    asyncio.run(main())
