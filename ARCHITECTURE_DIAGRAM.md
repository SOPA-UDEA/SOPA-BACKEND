# 🏗️ SOPA - Diagrama de Arquitectura

## 📋 Resumen de la Arquitectura

La aplicación SOPA está basada en una arquitectura de microservicios containerizados con Docker, desplegada en un servidor Ubuntu dedicado para producción.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           🌐 INTERNET / CLIENTS                                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                                    HTTP/HTTPS
                                         │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       🖥️ SERVIDOR UBUNTU DEDICADO                              │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                        📦 DOCKER CONTAINERS                             │   │
│  │                                                                         │   │
│  │  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐  │   │
│  │  │   🌐 NGINX      │────▶│  ⚡ FRONTEND     │     │  🔧 BACKEND     │  │   │
│  │  │  Reverse Proxy  │     │   Next.js       │     │   FastAPI       │  │   │
│  │  │  Load Balancer  │     │   (Port 3000)   │     │   (Port 8000)   │  │   │
│  │  │  (Port 80/443)  │     │                 │     │                 │  │   │
│  │  └─────────────────┘     └─────────────────┘     └─────────────────┘  │   │
│  │           │                        │                        │         │   │
│  │           │               HTTP API Calls                    │         │   │
│  │           │                        │                        │         │   │
│  │           └────────────────────────┼────────────────────────┘         │   │
│  │                                    │                                  │   │
│  │                                    │                                  │   │
│  │                     ┌──────────────┴──────────────┐                   │   │
│  │                     │                             │                   │   │
│  │                     │                             │                   │   │
│  │           ┌─────────────────────────────────────────────────┐         │   │
│  │           │              🗄️ PostgreSQL Database             │         │   │
│  │           │                  (Port 5432)                    │         │   │
│  │           │                                                 │         │   │
│  │           └─────────────────────────────────────────────────┘         │   │
│  │                                    │                                  │   │
│  │           ┌─────────────────────────────────────────────────┐         │   │
│  │           │               💾 Postgres Volume                │         │   │
│  │           │                 (Persistent)                    │         │   │
│  │           └─────────────────────────────────────────────────┘         │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                       🌐 DOCKER NETWORK                                │   │
│  │                      (sopa_network - bridge)                           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                         │
                              External Database Connection
                                         │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        ☁️ NEON DATABASE (Cloud)                                │
│                         (Para sincronización de datos)                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Componentes de la Arquitectura

### 🖥️ **Servidor de Producción**

- **OS**: Ubuntu Linux (Servidor Dedicado)
- **Container Runtime**: Docker + Docker Compose
- **Network**: Bridge Network (`sopa_network`)

### 🌐 **NGINX (Reverse Proxy)**

- **Imagen**: `nginx:alpine`
- **Puerto**: 80 (HTTP) / 443 (HTTPS)
- **Función**:
  - Reverse proxy para el backend
  - Load balancing
  - Rate limiting (10 req/s)
  - Security headers
  - SSL termination

### ⚡ **Frontend (Next.js)**

- **Framework**: Next.js
- **Container**: Docker
- **Puerto**: 3000 (interno)
- **Comunicación**: HTTP API calls al backend
- **Proxy**: A través de NGINX

### 🔧 **Backend (FastAPI)**

- **Framework**: FastAPI (Python)
- **Imagen**: Custom Dockerfile
- **Puerto**: 8000
- **Características**:
  - API RESTful
  - CORS habilitado
  - Prisma ORM
  - Módulos organizados:
    - Academic Program
    - Academic Schedule
    - Classroom
    - Group
    - Subject
    - Professor
    - Pensum

### 🗄️ **PostgreSQL Database**

- **Imagen**: `postgres:15-alpine`
- **Puerto**: 5432
- **Volumen**: `postgres_data_prod` (persistente)
- **Características**:
  - Health checks
  - Initialization scripts
  - Resource limits (1GB memory)
  - Connection pooling

### ☁️ **Neon Database (External)**

- **Función**: Sincronización de datos
- **Acceso**: Vía `NEON_DATABASE_URL`
- **Uso**: Scripts de sincronización de subjects

## 📊 Flujo de Datos

### 🔄 **Request Flow**

```
Cliente/Browser ──HTTP──▶ NGINX ──proxy_pass──▶ Backend (FastAPI)
                   │                                │
                   │                                ▼
                   │                           PostgreSQL DB
                   │                                │
                   ▼                                ▼
               Frontend (Next.js) ◀──JSON API─── Response
```

### 🗄️ **Database Sync Flow**

```
Neon DB (Cloud) ──SQL Sync──▶ Local PostgreSQL ──Prisma ORM──▶ FastAPI
```

## 🔒 Características de Seguridad

### 🛡️ **NGINX Security Headers**

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security`

### 🚦 **Rate Limiting**

- 10 requests/second por IP
- Burst: 20 requests
- Zone: 10MB memory

### 🔐 **Database Security**

- Password-protected PostgreSQL
- Environment variables para secrets
- Network isolation (Docker bridge)

## 📈 Características de Performance

### ⚡ **Optimización**

- Nginx proxy caching
- Database connection pooling
- Consultas optimizadas con Prisma ORM

### 🔧 **Resource Management**

- Memory limits por contenedor
- Health checks para auto-recovery
- Restart policies (always)

### 📊 **Monitoring & Logging**

- Health check endpoints
- Container logs via Docker
- Nginx access/error logs

## 🚀 Despliegue

### 🔄 **Development Environment**

```bash
docker-compose -f docker-compose.dev.yml up --build
```

### 🏭 **Production Environment**

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### 📦 **Container Management**

- **Development**: `sopa_*_dev` containers
- **Production**: `sopa_*_prod` containers
- **Networks**: Isolated bridge networks
- **Volumes**: Persistent data storage

## 🔧 Herramientas de Gestión

### 📝 **Database Management**

- Prisma CLI para migraciones
- Scripts de sincronización (`sync_subjects.py`)
- Backup/restore scripts
- Database seeding (`db_manager.py`)

### 🐳 **Docker Management**

- `docker-manager.bat` (Windows)
- Health checks automatizados
- Resource monitoring
- Log aggregation

## 🔄 Escalabilidad

### 📈 **Horizontal Scaling**

- Multiple backend containers (load balanced por NGINX)
- Database read replicas (futuro)

### 📊 **Vertical Scaling**

- Configuración de memory/CPU limits
- Database performance tuning

---

**Nota**: Esta arquitectura está optimizada para alta disponibilidad, seguridad y performance en un entorno de producción con capacidad de escalamiento futuro.
