#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de base de datos
"""
import os
import psycopg2
import subprocess
import sys


def run_command(cmd, shell=True):
    """Ejecutar comando y mostrar resultado"""
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def check_environment():
    """Verificar variables de entorno"""
    print("🔍 Checking environment variables...")

    database_url = os.getenv("DATABASE_URL")
    neon_url = os.getenv("NEON_DATABASE_URL")

    if database_url:
        print(f"✅ DATABASE_URL is set")
        # Ocultar password en la salida
        safe_url = database_url.split("@")[1] if "@" in database_url else database_url
        print(f"   Host: {safe_url}")
    else:
        print("❌ DATABASE_URL is not set")
        return False

    if neon_url:
        print("✅ NEON_DATABASE_URL is set")
    else:
        print("⚠️ NEON_DATABASE_URL is not set")

    return True


def test_db_connection():
    """Probar conexión a la base de datos"""
    print("🔍 Testing database connection...")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ No DATABASE_URL found")
        return False

    try:
        conn = psycopg2.connect(database_url, connect_timeout=10)
        cursor = conn.cursor()

        # Probar una consulta simple
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connection successful")
        print(f"   PostgreSQL version: {version[:50]}...")

        # Verificar tablas existentes
        cursor.execute(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """
        )

        tables = cursor.fetchall()
        if tables:
            print(f"✅ Found {len(tables)} tables:")
            for table in tables[:10]:  # Mostrar solo las primeras 10
                print(f"   - {table[0]}")
            if len(tables) > 10:
                print(f"   ... and {len(tables) - 10} more")
        else:
            print("⚠️ No tables found - migrations may not have run")

        cursor.close()
        conn.close()
        return True

    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def check_prisma_status():
    """Verificar estado de Prisma"""
    print("🔍 Checking Prisma status...")

    # Verificar si prisma está disponible
    success, stdout, stderr = run_command("npx prisma --version")
    if success:
        print("✅ Prisma CLI is available")
        print(f"   Version: {stdout.strip().split()[0] if stdout else 'Unknown'}")
    else:
        print(f"❌ Prisma CLI not available: {stderr}")
        return False

    # Verificar schema.prisma
    if os.path.exists("prisma/schema.prisma"):
        print("✅ prisma/schema.prisma found")
    else:
        print("❌ prisma/schema.prisma not found")
        return False

    # Verificar directorio de migraciones
    if os.path.exists("prisma/migrations"):
        migrations = os.listdir("prisma/migrations")
        migration_dirs = [
            d
            for d in migrations
            if os.path.isdir(f"prisma/migrations/{d}") and d != "__pycache__"
        ]
        print(f"✅ Found {len(migration_dirs)} migration(s)")
        for migration in migration_dirs[:5]:  # Mostrar solo las primeras 5
            print(f"   - {migration}")
    else:
        print("⚠️ No migrations directory found")

    return True


def check_network_connectivity():
    """Verificar conectividad de red"""
    print("🔍 Checking network connectivity...")

    # Probar conectividad al host de PostgreSQL
    database_url = os.getenv("DATABASE_URL", "")
    if "sopa_postgres_prod" in database_url:
        success, stdout, stderr = run_command("nc -zv sopa_postgres_prod 5432")
        if success:
            print("✅ Can reach PostgreSQL host")
        else:
            print(f"❌ Cannot reach PostgreSQL host: {stderr}")
            return False

    return True


def main():
    """Función principal de diagnóstico"""
    print("🏥 SOPA Database Diagnostics")
    print("=" * 40)

    all_good = True

    # Verificar entorno
    if not check_environment():
        all_good = False

    print()

    # Verificar conectividad de red
    if not check_network_connectivity():
        all_good = False

    print()

    # Probar conexión a BD
    if not test_db_connection():
        all_good = False

    print()

    # Verificar Prisma
    if not check_prisma_status():
        all_good = False

    print()
    print("=" * 40)

    if all_good:
        print("🎉 All checks passed! Database should be working.")
        print("\nTry running:")
        print("   npx prisma migrate deploy")
        print("   python3 scripts/alternative_seed.py")
    else:
        print("❌ Some issues found. Please address them before proceeding.")
        print("\nCommon solutions:")
        print(
            "   1. Restart containers: docker-compose -f docker-compose.prod.yml restart"
        )
        print("   2. Check .env.prod file")
        print("   3. Ensure PostgreSQL container is running: docker ps")


if __name__ == "__main__":
    main()
