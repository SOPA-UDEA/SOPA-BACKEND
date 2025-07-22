#!/bin/bash
#
# Docker Entrypoint Script for Production
# Handles migrations and smart database seeding
#

set -e

echo "🚀 Starting SOPA API Production Deployment..."

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database to be ready..."
    echo "📍 Using DATABASE_URL: ${DATABASE_URL}"
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        # Try simple connection test first
        if python3 -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), connect_timeout=5)
    conn.close()
    print('✅ Database connection successful!')
    exit(0)
except Exception as e:
    print(f'❌ Connection failed: {e}')
    exit(1)
        " 2>/dev/null; then
            echo "✅ Database connection successful!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "❌ Database not ready. Attempt $attempt/$max_attempts. Retrying in 2 seconds..."
        sleep 2
    done
    
    echo "❌ Failed to connect to database after $max_attempts attempts"
    echo "🔍 Debug info:"
    echo "DATABASE_URL: ${DATABASE_URL}"
    echo "POSTGRES_USER: ${POSTGRES_USER}"
    echo "POSTGRES_DB: ${POSTGRES_DB}"
    
    # Try to ping the database host
    echo "🌐 Testing network connectivity to postgres..."
    if command -v nc >/dev/null 2>&1; then
        nc -zv postgres 5432 || echo "❌ Cannot reach postgres:5432"
    fi
    
    exit 1
}

# Function to run migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    
    # Try npx prisma first
    if command -v npx >/dev/null 2>&1; then
        echo "🔧 Using npx prisma migrate deploy..."
        if npx prisma migrate deploy; then
            echo "✅ Migrations completed successfully!"
            return 0
        else
            echo "⚠️ npx prisma migrate deploy failed, trying alternative..."
        fi
    fi
    
    # Try alternative Python script
    if [ -f "scripts/run_migrations.py" ]; then
        echo "🔧 Using Python migration script..."
        if python3 scripts/run_migrations.py; then
            echo "✅ Migrations completed successfully!"
            return 0
        else
            echo "❌ Python migration script failed!"
        fi
    fi
    
    echo "❌ All migration methods failed!"
    exit 1
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
