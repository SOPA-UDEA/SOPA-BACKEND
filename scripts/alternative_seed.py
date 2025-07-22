#!/usr/bin/env python3
"""
Alternative seeding script that bypasses Prisma Python client
Uses direct database connections for initial seeding
"""

import os
import sys
import psycopg2
from psycopg2 import sql
import json


def get_database_url():
    """Get database URL from environment"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return database_url


def get_neon_database_url():
    """Get Neon database URL from environment"""
    neon_url = os.getenv('NEON_DATABASE_URL')
    if not neon_url:
        print("⚠️ NEON_DATABASE_URL not set, skipping subject sync")
        return None
    return neon_url


def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(get_database_url())
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def create_basic_data():
    """Create basic data without using Prisma"""
    print("🔄 Creating basic data...")
    
    try:
        conn = psycopg2.connect(get_database_url())
        cursor = conn.cursor()
        
        # Create basic academic schedules
        schedules = [
            (1, '2024-1', 'Semestre 2024-1'),
            (2, '2024-2', 'Semestre 2024-2'),
            (3, '2025-1', 'Semestre 2025-1')
        ]
        
        for schedule_id, code, name in schedules:
            cursor.execute("""
                INSERT INTO "AcademicSchedule" (id, code, name, "isActive")
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (schedule_id, code, name, schedule_id == 3))
        
        # Create basic academic programs
        programs = [
            (1, 'ING_SISTEMAS', 'Ingeniería de Sistemas'),
            (2, 'ING_INDUSTRIAL', 'Ingeniería Industrial'),
            (3, 'ING_CIVIL', 'Ingeniería Civil')
        ]
        
        for program_id, code, name in programs:
            cursor.execute("""
                INSERT INTO "AcademicProgram" (id, code, name)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (program_id, code, name))
        
        # Create some basic classrooms
        classrooms = [
            (1, 'AULA_101', 'Aula 101', 30),
            (2, 'AULA_102', 'Aula 102', 35),
            (3, 'LAB_COMP_1', 'Laboratorio de Computación 1', 25)
        ]
        
        for classroom_id, code, name, capacity in classrooms:
            cursor.execute("""
                INSERT INTO "Classroom" (id, code, name, capacity)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (classroom_id, code, name, capacity))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Basic data created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create basic data: {e}")
        return False


def sync_subjects_from_neon():
    """Sync subjects from Neon database"""
    neon_url = get_neon_database_url()
    if not neon_url:
        return True  # Skip if no Neon URL
    
    print("🔄 Syncing subjects from Neon...")
    
    try:
        # Connect to both databases
        local_conn = psycopg2.connect(get_database_url())
        neon_conn = psycopg2.connect(neon_url)
        
        local_cursor = local_conn.cursor()
        neon_cursor = neon_conn.cursor()
        
        # Get subjects from Neon
        neon_cursor.execute("""
            SELECT id, code, name, credits, "theoryHours", "labHours", "academicProgramId"
            FROM "Subject"
            LIMIT 100
        """)
        
        subjects = neon_cursor.fetchall()
        
        # Insert subjects into local database
        for subject in subjects:
            local_cursor.execute("""
                INSERT INTO "Subject" (id, code, name, credits, "theoryHours", "labHours", "academicProgramId")
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    code = EXCLUDED.code,
                    name = EXCLUDED.name,
                    credits = EXCLUDED.credits,
                    "theoryHours" = EXCLUDED."theoryHours",
                    "labHours" = EXCLUDED."labHours",
                    "academicProgramId" = EXCLUDED."academicProgramId"
            """, subject)
        
        local_conn.commit()
        
        local_cursor.close()
        neon_cursor.close()
        local_conn.close()
        neon_conn.close()
        
        print(f"✅ Synced {len(subjects)} subjects from Neon")
        return True
        
    except Exception as e:
        print(f"❌ Failed to sync subjects from Neon: {e}")
        print("💡 This might be normal if Neon database is not accessible")
        return True  # Don't fail the entire process


def verify_seeding():
    """Verify that seeding was successful"""
    print("🔍 Verifying seeding results...")
    
    try:
        conn = psycopg2.connect(get_database_url())
        cursor = conn.cursor()
        
        # Check counts
        tables_to_check = [
            'AcademicSchedule',
            'AcademicProgram', 
            'Classroom',
            'Subject'
        ]
        
        for table in tables_to_check:
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
            count = cursor.fetchone()[0]
            print(f"📊 {table}: {count} records")
        
        cursor.close()
        conn.close()
        
        print("✅ Seeding verification completed")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main seeding process"""
    print("🌱 Starting alternative database seeding (without Prisma Python)...")
    
    # Test connection
    if not test_connection():
        print("❌ Cannot connect to database")
        sys.exit(1)
    
    # Create basic data
    if not create_basic_data():
        print("❌ Failed to create basic data")
        sys.exit(1)
    
    # Sync subjects from Neon
    if not sync_subjects_from_neon():
        print("❌ Failed to sync subjects from Neon")
        # Don't exit - this might be expected in some environments
    
    # Verify results
    if not verify_seeding():
        print("❌ Seeding verification failed")
        sys.exit(1)
    
    print("🎉 Alternative database seeding completed successfully!")
    print("\n📋 Next steps:")
    print("1. Test the API: curl http://localhost:8000/health")
    print("2. Check API docs: http://localhost:8000/docs")
    print("3. Verify data in database")


if __name__ == "__main__":
    main()
