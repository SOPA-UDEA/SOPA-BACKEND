#!/usr/bin/env python3
"""
Script to mark migrations as applied without running them
This is used when tables are created manually via DBeaver
"""
import os
import psycopg2


def mark_migration_as_applied():
    """Mark the existing migration as applied in the _prisma_migrations table"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False

    try:
        conn = psycopg2.connect(database_url, connect_timeout=10)
        cursor = conn.cursor()

        # Check if _prisma_migrations table exists
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = '_prisma_migrations'
            )
        """
        )

        migrations_table_exists = cursor.fetchone()[0]

        if not migrations_table_exists:
            print("📋 Creating _prisma_migrations table...")
            cursor.execute(
                """
                CREATE TABLE "_prisma_migrations" (
                    "id" VARCHAR(36) NOT NULL,
                    "checksum" VARCHAR(64) NOT NULL,
                    "finished_at" TIMESTAMPTZ,
                    "migration_name" VARCHAR(255) NOT NULL,
                    "logs" TEXT,
                    "rolled_back_at" TIMESTAMPTZ,
                    "started_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
                    "applied_steps_count" INTEGER NOT NULL DEFAULT 0,
                    CONSTRAINT "_prisma_migrations_pkey" PRIMARY KEY ("id")
                )
            """
            )

        # Check if our migration is already recorded
        cursor.execute(
            """
            SELECT COUNT(*) FROM "_prisma_migrations" 
            WHERE migration_name = '20250708053558_init'
        """
        )

        migration_exists = cursor.fetchone()[0] > 0

        if not migration_exists:
            print("📝 Marking migration as applied...")
            # Insert the migration record
            cursor.execute(
                """
                INSERT INTO "_prisma_migrations" (
                    "id", 
                    "checksum", 
                    "finished_at", 
                    "migration_name", 
                    "logs", 
                    "applied_steps_count"
                ) VALUES (
                    gen_random_uuid()::text,
                    '75f44533a300de3c6c04a61f46b1adf3cfb3c15b96fd7a38a5e87ba9ad6af6e0',
                    now(),
                    '20250708053558_init',
                    'Migration applied manually via DBeaver',
                    1
                )
            """
            )
            print("✅ Migration marked as applied!")
        else:
            print("✅ Migration already marked as applied!")

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error marking migration: {e}")
        return False


def verify_tables():
    """Verify that all expected tables exist"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False

    try:
        conn = psycopg2.connect(database_url, connect_timeout=10)
        cursor = conn.cursor()

        # List of expected tables from the migration
        expected_tables = [
            "academic_program",
            "academic_schedule",
            "classroom",
            "classroom_x_group",
            "department",
            "faculty",
            "group",
            "group_x_professor",
            "mirror_group",
            "modality",
            "pensum",
            "prerequirement",
            "professor",
            "subject",
            "academic_schedule_pensum",
            "message_classroom_group",
            "message_type",
        ]

        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        )

        existing_tables = [row[0] for row in cursor.fetchall()]
        missing_tables = [
            table for table in expected_tables if table not in existing_tables
        ]

        print(f"📋 Found {len(existing_tables)} tables in database:")
        for table in existing_tables:
            print(f"   ✅ {table}")

        if missing_tables:
            print(f"⚠️ Missing {len(missing_tables)} expected tables:")
            for table in missing_tables:
                print(f"   ❌ {table}")
            return False
        else:
            print("✅ All expected tables are present!")
            return True

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False


if __name__ == "__main__":
    print("🔄 Verifying database schema...")

    if verify_tables():
        print("\n📝 Marking migration as applied...")
        if mark_migration_as_applied():
            print("🎉 Database is ready to use!")
        else:
            print("❌ Failed to mark migration as applied")
    else:
        print(
            "❌ Database schema incomplete. Please run the migration SQL in DBeaver first."
        )
