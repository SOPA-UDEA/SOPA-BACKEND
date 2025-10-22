# SOPA Backend Docker Implementation

This project includes a complete Docker setup for both development and production environments.

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Docker Compose v3.8 or higher

### Development Environment

1. **First time setup (clean rebuild):**

   ```bash
   $env:PATH += ";C:\Program Files\Docker\Docker\resources\bin"; .\scripts\docker\clean-rebuild.bat
   ```

2. **Start development environment:**

   ```bash
   .\scripts\docker\start-dev.bat
   ```

3. **Stop development environment:**
   ```bash
   .\scripts\docker\stop-dev.bat
   ```

### Production Environment

1. **Configure environment:**

   ```bash
   cp .env.prod.example .env.prod
   # Edit .env.prod with your production values
   ```

2. **Start production environment:**

   ```bash
   .\scripts\docker\start-prod.bat
   ```

3. **Stop production environment:**
   ```bash
   .\scripts\docker\stop-prod.bat
   ```

## Services

### Development

- **API**: http://localhost:8000 (FastAPI with hot reload)
- **Database**: localhost:5432 (PostgreSQL)
- **Redis**: localhost:6379 (Caching)

### Production

- **API**: http://localhost:8000 (FastAPI optimized)
- **Database**: Internal network only (PostgreSQL)
- **Redis**: Internal network only (Caching)
- **Nginx**: http://localhost:80 (Reverse proxy)

## Features

### Security (Production)

- Non-root user in containers
- Resource limits
- Security headers via Nginx
- Rate limiting
- Encrypted Redis

### Performance

- Multi-stage Docker builds
- Health checks
- Connection pooling
- Caching with Redis

### Development Features

- Hot reload
- Volume mounts for code changes
- Database persistence
- Easy setup scripts

## Database Management

### Migrations

Run Prisma migrations inside the container:

```bash
# Development
docker exec -it sopa_api_dev npx prisma migrate dev --name migration_name

# Production
docker exec -it sopa_api_prod npx prisma migrate deploy
```

### Database Seeding

Use the centralized database manager:

```bash
# Enter the container
docker exec -it sopa_api_dev bash

# Seed complete database (first time setup)
python scripts/db_manager.py seed

# Reset database
python scripts/db_manager.py reset

# Sync only subjects from Neon
python scripts/db_manager.py subjects

# Reset and seed (development)
python scripts/db_manager.py reset-seed
```

## Logs

View application logs:

```bash
docker-compose -f docker-compose.dev.yml logs -f api
```

View database logs:

```bash
docker-compose -f docker-compose.dev.yml logs -f postgres
```

## Troubleshooting

1. **Port conflicts**: Make sure ports 8000, 5432, and 6379 are not in use
2. **Permission issues**: Ensure Docker has proper permissions
3. **Database connection**: Wait for health checks to pass before accessing the API

## Environment Variables

### Development (.env.dev)

- Pre-configured for local development
- Default passwords (not secure)

### Production (.env.prod)

- **MUST** be configured before deployment
- Use secure passwords
- Configure allowed hosts
- Set proper database credentials
