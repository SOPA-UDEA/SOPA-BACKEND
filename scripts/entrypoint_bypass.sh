#!/bin/bash
#
# Bypass Entrypoint Script - Skips migrations when tables exist
# Use this when tables are already created manually via DBeaver
#

set -e

echo "🚀 Starting SOPA API with Migration Bypass..."

# Function to wait for database (Local PostgreSQL Container)
wait_for_db() {
    echo "⏳ Waiting for local PostgreSQL database to be ready..."
    echo "📍 Using DATABASE_URL: ${DATABASE_URL:0:50}..."
    echo "🖥️  Running on: $(uname -a)"
    
    max_attempts=15
    attempt=0
    
    echo "🔍 Testing local PostgreSQL database connection..."
    
    while [ $attempt -lt $max_attempts ]; do
        if python3 -c "
import os
import psycopg2
import sys
try:
    db_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(db_url, connect_timeout=10)
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
        echo "❌ Database not ready. Attempt $attempt/$max_attempts. Retrying in 2 seconds..."
        sleep 2
    done
    
    echo "❌ Failed to connect to database after $max_attempts attempts"
    exit 1
}

# Function to verify tables exist and mark migration as applied
verify_and_mark_migration() {
    echo "🔍 Verifying database schema..."
    
    if python3 scripts/mark_migration_applied.py; then
        echo "✅ Database schema verified and migration marked!"
        return 0
    else
        echo "⚠️ Database schema verification failed, but continuing..."
        return 0  # Don't fail the startup
    fi
}

# Function to start application directly
start_application() {
    echo "🚀 Starting FastAPI application directly..."
    exec gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
}

# Main execution flow - BYPASS MODE
main() {
    echo "🔄 BYPASS MODE: Skipping migrations (tables created manually)"
    wait_for_db
    verify_and_mark_migration
    start_application
}

# Execute main function
main
