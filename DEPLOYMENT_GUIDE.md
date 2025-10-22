# SOPA Backend - Guía de Despliegue

Esta guía proporciona instrucciones detalladas para desplegar el backend de SOPA en diferentes entornos.

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Configuración de Entorno](#configuración-de-entorno)
- [Despliegue en Desarrollo](#despliegue-en-desarrollo)
- [Despliegue en Producción](#despliegue-en-producción)
- [Gestión de Base de Datos](#gestión-de-base-de-datos)
- [Monitoreo y Logs](#monitoreo-y-logs)
- [Troubleshooting](#troubleshooting)

## 🛠️ Requisitos Previos

### Software Requerido

- **Docker**: >= 20.10.0
- **Docker Compose**: >= 2.0.0
- **Git**: Para clonar el repositorio
- **Node.js**: >= 18.0.0 (para Prisma CLI)

### Accesos Necesarios

- Acceso a la base de datos Neon (para sincronización de datos)
- Configuración de variables de entorno
- Puertos disponibles: 8000, 5432, 6379

## ⚙️ Configuración de Entorno

### 1. Variables de Entorno

#### Desarrollo (.env.dev)

```env
# Base de datos local (Docker)
DATABASE_URL="postgresql://sopa_user:sopa_pass@sopa_postgres_dev:5432/sopa_db"

# Base de datos Neon para sincronización
NEON_DATABASE_URL="postgresql://username:password@host:5432/database"

# Redis para cache
REDIS_URL="redis://sopa_redis_dev:6379"

# Configuración de aplicación
ENVIRONMENT="development"
DEBUG=true
LOG_LEVEL="debug"
```

#### Producción (.env.prod)

```env
# Base de datos de producción
DATABASE_URL="postgresql://prod_user:secure_pass@prod_host:5432/sopa_prod"

# Base de datos Neon para sincronización
NEON_DATABASE_URL="postgresql://username:password@host:5432/database"

# Redis de producción
REDIS_URL="redis://redis_host:6379"

# Configuración de aplicación
ENVIRONMENT="production"
DEBUG=false
LOG_LEVEL="info"
```

### 2. Archivos Docker

Los archivos de configuración Docker ya están incluidos:

- `docker-compose.dev.yml` - Configuración de desarrollo
- `docker-compose.prod.yml` - Configuración de producción
- `Dockerfile` - Imagen del backend
- `.dockerignore` - Archivos excluidos

## 🔧 Despliegue en Desarrollo

### Paso 1: Clonar y Configurar

```bash
# Clonar repositorio
git clone <repository-url>
cd SOPA-BACKEND

# Configurar variables de entorno
cp .env.dev.example .env.dev
# Editar .env.dev con tus configuraciones
```

### Paso 2: Construir y Ejecutar

```bash
# Construir e iniciar servicios
docker-compose -f docker-compose.dev.yml up --build

# O en modo detached (background)
docker-compose -f docker-compose.dev.yml up --build -d
```

### Paso 3: Configurar Base de Datos

```bash
# Entrar al contenedor del backend
docker exec -it sopa_api_dev bash

# Ejecutar migraciones de Prisma
npx prisma migrate deploy

# Verificar conexión a la base de datos
npx prisma db pull

# Poblar la base de datos (primera vez)
python scripts/db_manager.py seed
```

### Paso 4: Verificar Funcionamiento

```bash
# Verificar que el API esté funcionando
curl http://localhost:8000/health

# Acceder a la documentación
# http://localhost:8000/docs (Swagger UI)
```

## 🚀 Despliegue en Producción (Neon Cloud Database)

### Paso 1: Preparar Servidor

```bash
# En el servidor de producción
git clone <repository-url>
cd SOPA-BACKEND

# Configurar variables de entorno
cp .env.prod.example .env.prod
# Editar .env.prod con tu URL de Neon Database
```

**Configuración .env.prod para Neon:**

```env
# Neon Cloud Database - Tu database principal
DATABASE_URL="postgresql://username:password@your-neon-host:5432/database?sslmode=require"

# Si usas la misma base de datos para sync, usa la misma URL
NEON_DATABASE_URL="postgresql://username:password@your-neon-host:5432/database?sslmode=require"

# Redis y otras configuraciones
REDIS_URL="redis://redis:6379"
REDIS_PASSWORD=your_redis_password_here
ENVIRONMENT="production"
PROJECT_NAME="SOPA API - Production"
DEBUG=false
LOG_LEVEL="info"
API_PORT=8000
ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
```

### Paso 2: Configurar Firewall (si aplica)

```bash
# Abrir puertos necesarios
sudo ufw allow 8000  # API
sudo ufw allow 6379  # Redis (solo si es externo)
# No necesitas puerto 5432 porque usas Neon cloud database
```

### Paso 3: Desplegar

```bash
# Construir e iniciar en producción usando Neon database
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d

# Verificar que los contenedores estén ejecutándose (solo API y Redis)
docker ps

# Verificar variables de entorno del API
docker exec sopa_api_prod env | grep -E "(DATABASE_URL|NEON_DATABASE_URL)" | head -1
docker exec sopa_api_prod env | grep -E "(DATABASE_URL|POSTGRES_)"
```

### Paso 4: Configurar Base de Datos Neon

```bash
# Entrar al contenedor de producción
docker exec -it sopa_api_prod bash

# Método 1: Usando npx prisma (requiere Node.js en container)
npx prisma migrate deploy

# Método 2: Usando script Python mejorado para Neon
python scripts/fix_prisma_permissions.py

# Poblar datos iniciales en Neon (solo primera vez)
python3 scripts/alternative_seed.py
```

**Ventajas de usar Neon Cloud Database:**

- ✅ No hay contenedor PostgreSQL local que pueda fallar
- ✅ Base de datos gestionada con backups automáticos
- ✅ Escalabilidad automática
- ✅ Menor complejidad en Docker
- ✅ SSL habilitado por defecto
- ✅ Monitoreo y métricas incluidas

**Nota**: Al usar Neon, ya no necesitas gestionar un contenedor PostgreSQL. Tu base de datos está en la nube y es más robusta.

#### Solución de Problemas de Permisos

Si encuentras errores de permisos de Prisma Python:

````bash
# Arreglar permisos de Prisma
docker exec -it --user root sopa_api_prod python scripts/fix_prisma_permissions.py

# Alternativamente, usar seeding sin Prisma Python
docker exec -it sopa_api_prod python3 scripts/alternative_seed.py
```risma CLI automáticamente.

### Paso 5: Configurar Proxy Reverso (Opcional)

```nginx
# Nginx configuration example
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
````

## 🗄️ Gestión de Base de Datos

### Scripts de Gestión

El proyecto incluye un script centralizado para la gestión de la base de datos:

```bash
# Entrar al contenedor (desarrollo o producción)
docker exec -it sopa_api_dev bash  # o sopa_api_prod

# Comandos disponibles:
python scripts/db_manager.py seed        # Poblar base de datos completa
python scripts/db_manager.py reset       # Resetear base de datos
python scripts/db_manager.py subjects    # Sincronizar solo subjects
python scripts/db_manager.py reset-seed  # Resetear y poblar
```

### Flujo de Datos

1. **Prisma Migrate**: Gestiona el esquema de la base de datos
2. **Smart Seed**: Puebla datos básicos evitando duplicados
3. **Subject Sync**: Sincroniza subjects desde Neon usando SQL raw

### Sincronización de Subjects

El sistema utiliza un enfoque optimizado para sincronizar subjects:

```bash
# El script sync_subjects.py usa SQL raw para mayor eficiencia
# Se ejecuta automáticamente con 'python scripts/db_manager.py seed'
# O manualmente con:
python scripts/sync_subjects.py
```

### Backup y Restauración

```bash
# Backup de la base de datos
docker exec sopa_postgres_dev pg_dump -U sopa_user sopa_db > backup.sql

# Restaurar backup
docker exec -i sopa_postgres_dev psql -U sopa_user sopa_db < backup.sql
```

## 📊 Monitoreo y Logs

### Ver Logs

```bash
# Logs del backend
docker logs -f sopa_api_dev

# Logs de la base de datos
docker logs -f sopa_postgres_dev

# Logs de Redis
docker logs -f sopa_redis_dev

# Logs de todos los servicios
docker-compose -f docker-compose.dev.yml logs -f
```

### Health Checks

```bash
# Verificar salud del API
curl http://localhost:8000/health

# Verificar base de datos
docker exec sopa_postgres_dev pg_isready -U sopa_user

# Verificar Redis
docker exec sopa_redis_dev redis-cli ping
```

### Métricas de Performance

```bash
# Estadísticas de contenedores
docker stats

# Uso de espacio
docker system df

# Información detallada de contenedores
docker inspect sopa_api_dev
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos

```bash
# Verificar que PostgreSQL esté ejecutándose
docker ps | grep postgres

# Verificar logs de PostgreSQL
docker logs sopa_postgres_dev

# Probar conexión manualmente
docker exec sopa_postgres_dev pg_isready -U sopa_user
```

#### 2. Problemas con Migraciones de Prisma

```bash
# Resetear migraciones
npx prisma migrate reset

# Regenerar cliente de Prisma
npx prisma generate

# Aplicar migraciones manualmente
npx prisma migrate deploy
```

#### 3. Error en Sincronización de Subjects

```bash
# Verificar conexión a Neon
python -c "import psycopg2; conn = psycopg2.connect('your-neon-url'); print('OK')"

# Ejecutar sync con debug
python scripts/sync_subjects.py

# Verificar mapping de pensum
python -c "
import sys, os
sys.path.append('src')
from config import settings
print(settings.NEON_DATABASE_URL)
"
```

#### 4. Problemas de Puertos

```bash
# Verificar puertos en uso
netstat -tulpn | grep :8000

# Cambiar puerto en docker-compose si es necesario
# Editar docker-compose.dev.yml o docker-compose.prod.yml
```

### Comandos de Emergencia

```bash
# Parar todos los servicios
docker-compose -f docker-compose.dev.yml down

# Limpiar volúmenes (CUIDADO: elimina datos)
docker-compose -f docker-compose.dev.yml down -v

# Rebuild completo
docker-compose -f docker-compose.dev.yml up --build --force-recreate

# Limpiar sistema Docker
docker system prune -a
```

### Logs Detallados

```bash
# Habilitar logs detallados en el backend
# Editar .env.dev o .env.prod:
LOG_LEVEL="debug"
DEBUG=true

# Restart del servicio
docker-compose -f docker-compose.dev.yml restart backend
```

## 🔄 Actualizaciones

### Proceso de Actualización

1. **Backup de datos**
2. **Pull del código actualizado**
3. **Rebuild de contenedores**
4. **Ejecutar migraciones**
5. **Verificar funcionamiento**

```bash
# Ejemplo de actualización
docker-compose -f docker-compose.prod.yml down
git pull origin main
docker-compose -f docker-compose.prod.yml up --build -d
docker exec -it sopa_api_prod npx prisma migrate deploy
```

## 📞 Soporte

Para problemas adicionales:

1. Verificar logs detallados
2. Consultar documentación de Prisma
3. Revisar configuración de variables de entorno
4. Contactar al equipo de desarrollo

---

**Nota**: Esta guía asume configuraciones estándar. Ajusta según tu infraestructura específica.
