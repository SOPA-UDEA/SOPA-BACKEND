#!/usr/bin/env python3
"""
Alternative seeding script without Prisma Python dependencies.
Uses raw SQL and psycopg2 for database operations.
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

def get_database_url():
    """Get database URL from environment"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    return database_url

def connect_to_database():
    """Create database connection"""
    try:
        database_url = get_database_url()
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def create_basic_data(conn):
    """Create basic data using raw SQL"""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row['table_name'] for row in cursor.fetchall()]
        
        if not tables:
            print("❌ No tables found. Please run Prisma migrations first:")
            print("   npx prisma migrate deploy")
            return False
            
        print(f"✅ Found {len(tables)} tables")
        
        # Create Academic Schedules
        if 'academic_schedule' in tables:
            cursor.execute("""
                INSERT INTO academic_schedule (id, semester) 
                VALUES 
                    (1, '2024-1'),
                    (2, '2024-2'),
                    (3, '2025-1')
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Academic schedules created/verified")
        
        # Create Academic Programs
        if 'academic_program' in tables:
            cursor.execute("""
                INSERT INTO academic_program (id, code, name, "modalityAcademic", headquarter, version, "modalityId", "facultyId", "departmentId") 
                VALUES 
                    (1, 'ING-SIS', 'Ingeniería de Sistemas', 'Presencial', 'Medellín', 1, 1, 1, 1),
                    (2, 'ING-IND', 'Ingeniería Industrial', 'Presencial', 'Medellín', 1, 1, 1, 1),
                    (3, 'ING-CIV', 'Ingeniería Civil', 'Presencial', 'Medellín', 1, 1, 1, 1)
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Academic programs created/verified")
        
        # Create basic data for required foreign key tables first
        if 'faculty' in tables:
            cursor.execute("""
                INSERT INTO faculty (id, name) 
                VALUES (1, 'Facultad de Ingeniería')
                ON CONFLICT (id) DO NOTHING
            """)
        
        if 'department' in tables:
            cursor.execute("""
                INSERT INTO department (id, name) 
                VALUES (1, 'Departamento de Ingeniería de Sistemas')
                ON CONFLICT (id) DO NOTHING
            """)
            
        if 'modality' in tables:
            cursor.execute("""
                INSERT INTO modality (id, name) 
                VALUES (1, 'Presencial')
                ON CONFLICT (id) DO NOTHING
            """)
        
        # Create Pensums
        if 'pensum' in tables:
            cursor.execute("""
                INSERT INTO pensum (id, code, name, "academicProgramId") 
                VALUES 
                    (1, 'PENSUM-SIS-2023', 'Pensum Sistemas 2023', 1),
                    (2, 'PENSUM-IND-2023', 'Pensum Industrial 2023', 2),
                    (3, 'PENSUM-CIV-2023', 'Pensum Civil 2023', 3)
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Pensums created/verified")
        
        # Create basic Classrooms
        if 'classroom' in tables:
            cursor.execute("""
                INSERT INTO classroom (id, location, capacity, enabled) 
                VALUES 
                    (1, 'A101', 30, true),
                    (2, 'A102', 25, true),
                    (3, 'B201', 40, true),
                    (4, 'LAB1', 20, true)
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Classrooms created/verified")
        
        # Create Professors
        if 'professor' in tables:
            cursor.execute("""
                INSERT INTO professor (id, "firstName", "lastName", email, document) 
                VALUES 
                    (1, 'Juan', 'Pérez', 'juan.perez@udea.edu.co', '12345678'),
                    (2, 'María', 'González', 'maria.gonzalez@udea.edu.co', '87654321'),
                    (3, 'Carlos', 'Rodríguez', 'carlos.rodriguez@udea.edu.co', '11223344')
                ON CONFLICT (id) DO NOTHING
            """)
            print("✅ Professors created/verified")
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to create basic data: {e}")
        return False
    finally:
        cursor.close()

def sync_subjects_from_neon(conn):
    """Sync subjects from Neon database"""
    neon_url = os.getenv('NEON_DATABASE_URL')
    if not neon_url:
        print("⚠️ NEON_DATABASE_URL not found, skipping subject sync")
        return True
    
    try:
        # Connect to Neon
        neon_conn = psycopg2.connect(neon_url)
        neon_cursor = neon_conn.cursor(cursor_factory=RealDictCursor)
        
        # Get subjects from Neon
        neon_cursor.execute("""
            SELECT 
                codigo_materia,
                nombre,
                creditos,
                semestre,
                tipologia,
                programa
            FROM subjects 
            WHERE programa IS NOT NULL
            LIMIT 100
        """)
        
        subjects = neon_cursor.fetchall()
        neon_cursor.close()
        neon_conn.close()
        
        if not subjects:
            print("⚠️ No subjects found in Neon database")
            return True
        
        # Insert subjects into local database
        local_cursor = conn.cursor()
        
        for subject in subjects:
            try:
                local_cursor.execute("""
                    INSERT INTO "Subject" (
                        code, name, credits, semester, 
                        typology, "pensumId", "createdAt", "updatedAt"
                    ) VALUES (
                        %s, %s, %s, %s, %s, 1, NOW(), NOW()
                    ) ON CONFLICT (code) DO UPDATE SET
                        name = EXCLUDED.name,
                        credits = EXCLUDED.credits,
                        semester = EXCLUDED.semester,
                        typology = EXCLUDED.typology,
                        "updatedAt" = NOW()
                """, (
                    subject['codigo_materia'],
                    subject['nombre'],
                    subject['creditos'] or 3,
                    subject['semestre'] or 1,
                    subject['tipologia'] or 'Obligatoria'
                ))
            except Exception as e:
                print(f"⚠️ Error inserting subject {subject['codigo_materia']}: {e}")
                continue
        
        conn.commit()
        local_cursor.close()
        
        print(f"✅ Synced {len(subjects)} subjects from Neon")
        return True
        
    except Exception as e:
        print(f"⚠️ Failed to sync subjects from Neon: {e}")
        return True  # Don't fail the entire process

def main():
    """Main seeding function"""
    print("🌱 Starting alternative database seeding (without Prisma Python)...")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        sys.exit(1)
    
    print("✅ Database connection successful")
    
    # Create basic data
    print("🔄 Creating basic data...")
    if not create_basic_data(conn):
        print("❌ Failed to create basic data")
        conn.close()
        sys.exit(1)
    
    print("✅ Basic data created successfully")
    
    # Sync subjects from Neon
    print("🔄 Syncing subjects from Neon...")
    sync_subjects_from_neon(conn)
    
    # Close connection
    conn.close()
    
    print("🎉 Alternative seeding completed successfully!")

if __name__ == "__main__":
    main()