#!/usr/bin/env python3
"""
Subject Database Sync Script
Syncs subject data from Neon cloud database to local Docker database using raw SQL
Raw SQL approach bypasses Prisma GraphQL issues entirely
"""

import asyncio
import json
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from config import settings


def get_db_connection_params(database_url, require_ssl=True):
    """Parse database URL into connection parameters"""
    # Example: postgresql://user:pass@host:port/dbname
    import urllib.parse

    parsed = urllib.parse.urlparse(database_url)

    params = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": urllib.parse.unquote(parsed.username) if parsed.username else None,
        "password": urllib.parse.unquote(parsed.password) if parsed.password else None,
        "database": (
            parsed.path[1:] if parsed.path else "postgres"
        ),  # Remove leading slash
    }

    if require_ssl:
        params["sslmode"] = "require"

    return params


async def sync_subjects():
    """Sync subjects from Neon cloud database to local database using raw SQL"""

    print("🔗 Setting up database connections...")

    # Get connection parameters
    neon_params = get_db_connection_params(settings.NEON_DATABASE_URL, require_ssl=True)
    local_params = get_db_connection_params(settings.DATABASE_URL, require_ssl=False)

    neon_conn = None
    local_conn = None

    try:
        # Connect to Neon database
        print("📡 Connecting to Neon database...")
        neon_conn = psycopg2.connect(**neon_params)
        neon_cur = neon_conn.cursor(cursor_factory=RealDictCursor)

        # Connect to local database
        print("🏠 Connecting to local database...")
        local_conn = psycopg2.connect(**local_params)
        local_cur = local_conn.cursor(cursor_factory=RealDictCursor)

        # Build pensum mapping using raw SQL
        print("🗺️ Building pensum mapping...")

        # Get pensum data with academic program codes
        neon_cur.execute(
            """
            SELECT p.id as neon_id, p.version, ap.code as program_code
            FROM pensum p
            JOIN academic_program ap ON p."academicProgramId" = ap.id
        """
        )
        neon_pensum_data = neon_cur.fetchall()

        local_cur.execute(
            """
            SELECT p.id as local_id, p.version, ap.code as program_code
            FROM pensum p
            JOIN academic_program ap ON p."academicProgramId" = ap.id
        """
        )
        local_pensum_data = local_cur.fetchall()

        # Create mapping: (program_code, version) -> local_pensum_id
        pensum_mapping = {}
        for local_pensum in local_pensum_data:
            key = (local_pensum["program_code"], local_pensum["version"])
            pensum_mapping[key] = local_pensum["local_id"]

        print(f"📊 Built mapping for {len(pensum_mapping)} local pensum records")

        # Get subjects from Neon with pensum info
        print("📚 Fetching subjects from Neon...")
        neon_cur.execute(
            """
            SELECT 
                s.id,
                s.name,
                s.code,
                s.credits,
                s."weeklyHours",
                s.weeks,
                s.level,
                s.fields,
                s.validable,
                s.enableable,
                s."coRequirements",
                s."creditRequirements",
                s."pensumId",
                p.version as pensum_version,
                ap.code as program_code
            FROM subject s
            JOIN pensum p ON s."pensumId" = p.id
            JOIN academic_program ap ON p."academicProgramId" = ap.id
            ORDER BY s.id
        """
        )
        neon_subjects = neon_cur.fetchall()

        print(f"📊 Found {len(neon_subjects)} subjects in Neon")

        # Check how many subjects already exist locally
        local_cur.execute("SELECT COUNT(*) as count FROM subject")
        local_count = local_cur.fetchone()["count"]
        print(f"📊 Current local subjects: {local_count}")

        # Process subjects in batches
        batch_size = 100
        successful_inserts = 0
        failed_inserts = 0

        for i in range(0, len(neon_subjects), batch_size):
            batch = neon_subjects[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(neon_subjects) + batch_size - 1) // batch_size

            print(
                f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} subjects)..."
            )

            for subject in batch:
                try:
                    # Find local pensum ID
                    pensum_key = (subject["program_code"], subject["pensum_version"])
                    local_pensum_id = pensum_mapping.get(pensum_key)

                    if not local_pensum_id:
                        print(
                            f"⚠️ Skipping subject {subject['code']}: no local pensum for {pensum_key}"
                        )
                        failed_inserts += 1
                        continue

                    # Check if subject already exists
                    local_cur.execute(
                        "SELECT id FROM subject WHERE code = %s", (subject["code"],)
                    )
                    if local_cur.fetchone():
                        # print(f"⏭️ Skipping subject {subject['code']}: already exists")
                        continue

                    # Prepare fields JSON
                    fields_json = subject["fields"]
                    if fields_json is None:
                        fields_json = {}
                    elif isinstance(fields_json, str):
                        try:
                            fields_json = json.loads(fields_json)
                        except:
                            fields_json = {"raw_value": fields_json}

                    # Insert subject using raw SQL
                    insert_sql = """
                        INSERT INTO subject (
                            name, code, credits, "weeklyHours", weeks, level, fields,
                            validable, enableable, "coRequirements", "creditRequirements", "pensumId"
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s
                        )
                    """

                    local_cur.execute(
                        insert_sql,
                        (
                            subject["name"],
                            subject["code"],
                            subject["credits"],
                            subject["weeklyHours"],
                            subject["weeks"],
                            subject["level"],
                            json.dumps(fields_json),  # Convert to JSON string
                            subject["validable"],
                            subject["enableable"],
                            subject["coRequirements"],
                            subject["creditRequirements"],
                            local_pensum_id,
                        ),
                    )

                    successful_inserts += 1

                    # Commit every 50 successful inserts
                    if successful_inserts % 50 == 0:
                        local_conn.commit()
                        print(f"✅ Committed {successful_inserts} subjects so far...")

                except Exception as e:
                    print(f"❌ Error inserting subject {subject['code']}: {e}")
                    failed_inserts += 1
                    # Continue with next subject
                    continue

        # Final commit
        local_conn.commit()

        # Final count
        local_cur.execute("SELECT COUNT(*) as count FROM subject")
        final_count = local_cur.fetchone()["count"]

        print(f"\n🎉 Subject sync completed!")
        print(f"✅ Successfully inserted: {successful_inserts}")
        print(f"❌ Failed inserts: {failed_inserts}")
        print(f"📊 Total subjects before: {local_count}")
        print(f"📊 Total subjects after: {final_count}")
        print(f"📊 Net increase: {final_count - local_count}")

    except Exception as e:
        print(f"❌ Fatal error during raw SQL sync: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Close connections
        if neon_conn:
            neon_conn.close()
            print("📡 Closed Neon connection")
        if local_conn:
            local_conn.close()
            print("🏠 Closed local connection")


if __name__ == "__main__":
    asyncio.run(sync_subjects())
