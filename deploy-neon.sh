#!/bin/bash
#
# Deploy SOPA Backend to Production with Neon Database
# 
# This script deploys the application using only Neon cloud database
# No local PostgreSQL container needed
#

set -e

echo "🚀 SOPA Backend - Deploying to Production with Neon Database"
echo "============================================================"

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "❌ Error: .env.prod file not found!"
    echo "📝 Please copy .env.prod.example to .env.prod and configure your Neon database URL"
    echo "   cp .env.prod.example .env.prod"
    exit 1
fi

# Validate Neon DATABASE_URL is set
if ! grep -q "DATABASE_URL=" .env.prod || grep -q "your-neon-host" .env.prod; then
    echo "❌ Error: Please configure your Neon DATABASE_URL in .env.prod"
    echo "📝 Example: DATABASE_URL=\"postgresql://user:pass@host:5432/db?sslmode=require\""
    exit 1
fi

echo "✅ Environment configuration found"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Clean up old images (optional)
echo "🧹 Cleaning up old images..."
docker rmi sopa-backend_api 2>/dev/null || true

# Build and start with Neon
echo "🏗️  Building and starting with Neon database..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d

# Wait a moment for containers to start
echo "⏳ Waiting for containers to initialize..."
sleep 10

# Check container status
echo "🔍 Checking container status..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test API connectivity
echo "🌐 Testing API connectivity..."
sleep 5
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✅ API is responding!"
else
    echo "⚠️  API may still be starting up. Check logs with:"
    echo "   docker logs -f sopa_api_prod"
fi

# Display useful commands
echo ""
echo "🎉 Deployment completed!"
echo "================================================"
echo "📊 Monitor with:"
echo "   docker logs -f sopa_api_prod"
echo "   docker stats"
echo ""
echo "🔧 Manage database:"
echo "   docker exec -it sopa_api_prod bash"
echo "   python scripts/fix_prisma_permissions.py"
echo ""
echo "🌐 Access API:"
echo "   http://localhost:8000"
echo "   http://localhost:8000/docs"
echo ""
echo "🛑 Stop deployment:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo "================================================"
