#!/usr/bin/env python3
"""
Simple script to list database tables
"""
import os
import psycopg2


def list_tables():
    """List all tables in the database"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return

    try:
        conn = psycopg2.connect(database_url, connect_timeout=10)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute(
            """
            SELECT table_name, 
                   table_type,
                   (SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = t.table_name 
                    AND table_schema = 'public') as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        )

        tables = cursor.fetchall()

        if tables:
            print(f"📋 Found {len(tables)} table(s) in database:")
            print("-" * 60)
            print(f"{'Table Name':<30} {'Type':<10} {'Columns':<10}")
            print("-" * 60)

            for table_name, table_type, column_count in tables:
                print(f"{table_name:<30} {table_type:<10} {column_count:<10}")

            print("-" * 60)

            # Show a sample table structure
            if tables:
                sample_table = tables[0][0]
                print(f"\n🔍 Structure of '{sample_table}' table:")
                cursor.execute(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """,
                    (sample_table,),
                )

                columns = cursor.fetchall()
                if columns:
                    print(f"{'Column':<25} {'Type':<15} {'Nullable':<10} {'Default'}")
                    print("-" * 70)
                    for col_name, data_type, nullable, default in columns:
                        default_str = str(default)[:20] if default else ""
                        print(
                            f"{col_name:<25} {data_type:<15} {nullable:<10} {default_str}"
                        )

        else:
            print("⚠️ No tables found in database")
            print("💡 You need to run migrations first:")
            print("   - Execute the migration SQL in DBeaver, or")
            print("   - Fix the Prisma CLI network issues")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    list_tables()
