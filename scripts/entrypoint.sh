#!/bin/bash
"""
Docker Entrypoint Script for Production
Handles migrations and smart database seeding
"""

set -e

echo "🚀 Starting SOPA API Production Deployment..."

# Function to wait for database
wait_for_db() {
    echo "⏳ Waiting for database to be ready..."
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if python -c "
import asyncio
from src.database import database

async def test_connection():
    try:
        await database.connect()
        await database.disconnect()
        return True
    except:
        return False

result = asyncio.run(test_connection())
exit(0 if result else 1)
        "; then
            echo "✅ Database connection successful!"
            break
        fi
        
        attempt=$((attempt + 1))
        echo "❌ Database not ready. Attempt $attempt/$max_attempts. Retrying in 2 seconds..."
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Failed to connect to database after $max_attempts attempts"
        exit 1
    fi
}

# Function to run migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    
    if prisma migrate deploy; then
        echo "✅ Migrations completed successfully!"
    else
        echo "❌ Migration failed!"
        exit 1
    fi
}

# Function to run smart seeding
run_smart_seeding() {
    echo "🌱 Running smart database seeding..."
    
    if python scripts/smart_seed.py; then
        echo "✅ Smart seeding completed!"
    else
        echo "❌ Smart seeding failed!"
        exit 1
    fi
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
