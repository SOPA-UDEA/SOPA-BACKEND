#!/bin/bash
#
# Docker Entrypoint Script for Production
# Handles migrations and smart database seeding
#

set -e

echo "🚀 Starting SOPA API Production Deployment..."

# Function to wait for database (Neon Cloud Database)
wait_for_db() {
    echo "⏳ Waiting for Neon cloud database to be ready..."
    echo "📍 Using DATABASE_URL: ${DATABASE_URL:0:50}..."
    echo "🖥️  Running on: $(uname -a)"
    
    max_attempts=30  # Reduced since we're connecting to a cloud database
    attempt=0
    
    echo "🔍 Testing Neon database connection..."
    
    while [ $attempt -lt $max_attempts ]; do
        # Test connection to Neon database
        if python3 -c "
import os
import psycopg2
import sys
try:
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL is not set')
        sys.exit(1)
    
    print('🔍 Connecting to Neon database...')
    conn = psycopg2.connect(
        db_url, 
        connect_timeout=15,
        application_name='sopa_api_startup',
        sslmode='require'  # Neon requires SSL
    )
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()[0]
    print('✅ Connected to Neon PostgreSQL:', version[:60] + '...')
    cursor.close()
    conn.close()
    sys.exit(0)
except Exception as e:
    print('❌ Neon connection failed:', str(e))
    sys.exit(1)
        " 2>&1; then
            echo "✅ Neon database connection successful!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "❌ Neon database not ready. Attempt $attempt/$max_attempts. Retrying in 5 seconds..."
        sleep 5
    done
    
    echo "❌ Failed to connect to Neon database after $max_attempts attempts"
    echo "🔍 Final debug info:"
    echo "DATABASE_URL: ${DATABASE_URL:0:50}..."
    echo "Container hostname: $(hostname)"
    echo "Container IP: $(hostname -I 2>/dev/null || echo 'Unknown')"
    
    # Network debugging for external connectivity
    echo "🌐 Network debugging:"
    if command -v curl >/dev/null 2>&1; then
        echo "Testing external connectivity:"
        curl -I --connect-timeout 10 https://google.com || echo "External connectivity test failed"
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
