#!/usr/bin/env python3
"""
Script para arreglar permisos de Prisma Python en contenedores Docker
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, shell=False):
    """Ejecutar comando y retornar resultado"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def fix_prisma_permissions():
    """Arreglar permisos de Prisma Python"""
    print("🔧 Fixing Prisma Python permissions...")
    
    # Directorios que necesitan permisos correctos
    cache_dirs = [
        "/root/.cache",
        "/home/appuser/.cache", 
        "/app/.cache",
        os.path.expanduser("~/.cache")
    ]
    
    for cache_dir in cache_dirs:
        try:
            # Crear directorio si no existe
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {cache_dir}")
            
            # Intentar cambiar permisos
            success, stdout, stderr = run_command(['chmod', '-R', '755', cache_dir])
            if success:
                print(f"✅ Fixed permissions for: {cache_dir}")
            else:
                print(f"⚠️ Could not fix permissions for {cache_dir}: {stderr}")
                
        except Exception as e:
            print(f"⚠️ Error with directory {cache_dir}: {e}")
    
    # Limpiar cache existente de Prisma si tiene problemas
    prisma_cache_dirs = [
        "/root/.cache/prisma-python",
        "/home/appuser/.cache/prisma-python",
        "/app/.cache/prisma-python"
    ]
    
    for prisma_dir in prisma_cache_dirs:
        if os.path.exists(prisma_dir):
            try:
                print(f"🧹 Cleaning Prisma cache: {prisma_dir}")
                shutil.rmtree(prisma_dir)
                print(f"✅ Cleaned: {prisma_dir}")
            except Exception as e:
                print(f"⚠️ Could not clean {prisma_dir}: {e}")
    
    # Intentar generar cliente Prisma con timeout
    print("🔄 Regenerating Prisma client...")
    success, stdout, stderr = run_command(['timeout', '30s', 'npx', 'prisma', 'generate'])
    if success:
        print("✅ Prisma client regenerated successfully")
        print(f"Output: {stdout[:200]}...")
    else:
        print(f"⚠️ Failed to regenerate Prisma client: {stderr}")
        # Intentar sin timeout
        print("🔄 Trying without timeout...")
        success2, stdout2, stderr2 = run_command(['npx', 'prisma', 'generate'])
        if success2:
            print("✅ Prisma client regenerated successfully (without timeout)")
        else:
            print(f"⚠️ Still failed: {stderr2}")

def run_migrations():
    """Ejecutar migraciones de Prisma con manejo de errores"""
    print("🔄 Running Prisma migrations...")
    
    # Intentar con timeout primero
    success, stdout, stderr = run_command(['timeout', '60s', 'npx', 'prisma', 'migrate', 'deploy'])
    if success:
        print("✅ Migrations completed successfully")
        print(f"Output: {stdout[-300:]}")  # Mostrar últimas líneas
        return True
    else:
        print(f"⚠️ Migrations failed or timed out: {stderr}")
        
        # Intentar sin timeout
        print("🔄 Trying migrations without timeout...")
        success2, stdout2, stderr2 = run_command(['npx', 'prisma', 'migrate', 'deploy'])
        if success2:
            print("✅ Migrations completed successfully (without timeout)")
            return True
        else:
            print(f"❌ Migrations failed completely: {stderr2}")
            return False

def check_database_tables():
    """Verificar que las tablas existan en la base de datos"""
    print("🔍 Checking database tables...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    print(f"📍 Using DATABASE_URL: {database_url.split('@')[1] if '@' in database_url else 'Invalid URL'}")
    
    try:
        import psycopg2
        conn = psycopg2.connect(database_url, connect_timeout=10)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        if tables:
            print(f"✅ Found {len(tables)} tables in database:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("❌ No tables found in database - migrations not run yet")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("⚠️ psycopg2 not available, cannot check tables directly")
        return True
    except psycopg2.OperationalError as e:
        if "role" in str(e) and "does not exist" in str(e):
            print(f"❌ Database user does not exist: {e}")
            print("💡 Check POSTGRES_USER in .env.prod file")
        elif "database" in str(e) and "does not exist" in str(e):
            print(f"❌ Database does not exist: {e}")
            print("💡 Check POSTGRES_DB in .env.prod file")
        else:
            print(f"❌ Database connection failed: {e}")
            print("💡 Check DATABASE_URL and ensure PostgreSQL is running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_environment():
    """Verificar configuración de entorno"""
    print("🔍 Checking environment configuration...")
    
    required_vars = ['DATABASE_URL', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var} is not set")
        else:
            # Ocultar passwords en la salida
            display_value = "****" if "PASSWORD" in var else value[:50] + "..." if len(value) > 50 else value
            print(f"✅ {var} = {display_value}")
    
    if missing_vars:
        print(f"\n💡 Missing environment variables: {', '.join(missing_vars)}")
        print("   Create or update .env.prod file with these variables")
        return False
    
    return True

def main():
    """Función principal que ejecuta todo el proceso"""
    print("🚀 SOPA Database Setup Script")
    print("=" * 40)
    
    # 0. Verificar variables de entorno
    if not check_environment():
        print("\n❌ Environment configuration issues found.")
        print("   Please check and update your .env.prod file")
        return
    
    print()
    
    # 1. Arreglar permisos
    fix_prisma_permissions()
    print()
    
    # 2. Ejecutar migraciones
    if run_migrations():
        print()
        # 3. Verificar tablas
        check_database_tables()
        print()
        
        # 4. Sugerir próximos pasos
        print("🎯 Next steps:")
        print("   1. Run: python3 scripts/alternative_seed.py")
        print("   2. Or run: python3 scripts/db_manager.py seed")
        print("   3. Check API health: curl http://localhost:8000/health")
    else:
        print("\n❌ Could not complete migrations. Try manual approach:")
        print("   1. Check database logs: docker logs sopa_postgres_prod")
        print("   2. Check .env.prod configuration")
        print("   3. Restart containers: docker-compose -f docker-compose.prod.yml restart")
        print("   4. Try direct SQL approach")

if __name__ == "__main__":
    main()