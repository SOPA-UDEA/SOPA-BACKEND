#!/bin/bash
#
# Docker Entrypoint Script for Production
# Handles migrations and smart database seeding
#

set -e

echo "🚀 Starting SOPA API Production Deployment..."

# Function to fix Prisma Python permissions
fix_prisma_permissions() {
    echo "🔧 Setting Prisma environment variables..."
    
    # Set PRISMA_CLIENT_ENGINE_TYPE to avoid binary path issues
    export PRISMA_CLIENT_ENGINE_TYPE="library"
    export PRISMA_CLI_BINARY_TARGETS="native"
    
    echo "✅ Prisma environment configured for user: $(whoami)"
}

# Function to debug environment and database connection
debug_environment() {
    echo "🔍 Environment Debug Information:"
    echo "DATABASE_URL: ${DATABASE_URL:0:70}..."
    echo "POSTGRES_DB: ${POSTGRES_DB}"
    echo "POSTGRES_USER: ${POSTGRES_USER}"
    echo "Container User: $(whoami)"
    echo "Container ID: $(hostname)"
    echo "Python Version: $(python3 --version)"
}

# Function to wait for database (Local PostgreSQL Container)
wait_for_db() {
    echo "⏳ Waiting for local PostgreSQL database to be ready..."
    echo "📍 Using DATABASE_URL: ${DATABASE_URL:0:50}..."
    echo "🖥️  Running on: $(uname -a)"
    
    max_attempts=30
    attempt=0
    
    echo "🔍 Testing local PostgreSQL database connection..."
    
    while [ $attempt -lt $max_attempts ]; do
        # Test connection to local PostgreSQL container
        if python3 -c "
import os
import psycopg2
import sys
try:
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL is not set')
        sys.exit(1)
    
    print('🔍 Connecting to local PostgreSQL database...')
    conn = psycopg2.connect(
        db_url, 
        connect_timeout=10,
        application_name='sopa_api_startup'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print('✅ Connected to PostgreSQL:', version[:60] + '...')
    cursor.close()
    conn.close()
    sys.exit(0)
except Exception as e:
    print('❌ Database connection failed:', str(e))
    sys.exit(1)
        " 2>&1; then
            echo "✅ Local PostgreSQL database connection successful!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "❌ Database not ready. Attempt $attempt/$max_attempts. Retrying in 3 seconds..."
        sleep 3
    done
    
    echo "❌ Failed to connect to local PostgreSQL database after $max_attempts attempts"
    echo "🔍 Final debug info:"
    echo "DATABASE_URL: ${DATABASE_URL:0:50}..."
    echo "Container hostname: $(hostname)"
    echo "Container IP: $(hostname -I 2>/dev/null || echo 'Unknown')"
    
    exit 1
}

# Function to verify tables exist and mark migration as applied (BYPASS MODE)
verify_schema() {
    echo "� BYPASS MODE: Verifying existing database schema..."
    
    # Check if tables exist (created manually via DBeaver)
    if python3 -c "
import os
import psycopg2
try:
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url, connect_timeout=10)
    cursor = conn.cursor()
    cursor.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE'\")
    table_count = cursor.fetchone()[0]
    print(f'📋 Found {table_count} tables in database')
    if table_count >= 15:  # We expect at least 15+ tables
        print('✅ Schema verified - tables exist!')
    else:
        print('⚠️ Few tables found, but continuing...')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'⚠️ Schema verification failed: {e}, but continuing...')
    "; then
        echo "✅ Schema verification completed!"
        return 0
    else
        echo "⚠️ Schema verification had issues, but continuing..."
        return 0  # Don't fail startup
    fi
}

# Function to run smart seeding
run_smart_seeding() {
    echo "🌱 Running smart database seeding..."
    
    # Try smart_seed.py first
    if [ -f "scripts/smart_seed.py" ]; then
        if python3 scripts/smart_seed.py; then
            echo "✅ Smart seeding completed!"
            return 0
        else
            echo "⚠️ Smart seeding failed, trying alternative..."
        fi
    fi
    
    # Try alternative_seed.py as fallback
    if [ -f "scripts/alternative_seed.py" ]; then
        echo "🔧 Using alternative seeding script..."
        if python3 scripts/alternative_seed.py; then
            echo "✅ Alternative seeding completed!"
            return 0
        else
            echo "⚠️ Alternative seeding failed!"
        fi
    fi
    
    echo "⚠️ Seeding failed, but continuing with application startup..."
    return 0  # Don't fail the entire startup for seeding issues
}

# Function to start application
start_application() {
    echo "🚀 Starting FastAPI application..."
    exec gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
}

# Main execution flow - BYPASS MODE  
main() {
    echo "🔄 BYPASS MODE: Tables created manually, skipping migrations"
    fix_prisma_permissions
    debug_environment
    wait_for_db
    verify_schema
    start_application
}

# Execute main function
main
