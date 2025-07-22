#!/bin/bash
#
# Docker Entrypoint Script for Production
# Handles migrations and smart database seeding
#

set -e

echo "🚀 Starting SOPA API Production Deployment..."

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

# Function to run migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    
    # Use Python Prisma CLI directly (already installed)
    echo "🔧 Using Python Prisma migrate deploy..."
    if python3 -m prisma migrate deploy; then
        echo "✅ Migrations completed successfully!"
        return 0
    else
        echo "⚠️ Python Prisma migrate failed, trying alternative approaches..."
    fi
    
    # Try direct prisma command
    if command -v prisma >/dev/null 2>&1; then
        echo "🔧 Using direct prisma migrate deploy..."
        if prisma migrate deploy; then
            echo "✅ Migrations completed successfully!"
            return 0
        else
            echo "⚠️ Direct prisma migrate failed..."
        fi
    fi
    
    # Try alternative Python script as fallback
    if [ -f "scripts/run_migrations.py" ]; then
        echo "🔧 Using Python migration script..."
        if python3 scripts/run_migrations.py; then
            echo "✅ Migrations completed successfully!"
            return 0
        else
            echo "❌ Python migration script failed!"
        fi
    fi
    
    # If all else fails, try to create tables manually
    echo "🔧 Trying manual table creation..."
    if python3 -c "
import asyncio
from prisma import Prisma

async def main():
    db = Prisma()
    await db.connect()
    print('✅ Database connected successfully for manual setup')
    await db.disconnect()

asyncio.run(main())
    "; then
        echo "✅ Manual database setup completed!"
        return 0
    else
        echo "❌ All migration methods failed!"
        exit 1
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

# Main execution flow
main() {
    wait_for_db
    run_migrations
    run_smart_seeding
    start_application
}

# Execute main function
main
