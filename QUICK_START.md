# 🚀 SOPA Backend - Inicio Rápido

¡Bienvenido al backend de SOPA! Este documento te ayudará a poner en marcha el sistema rápidamente.

## ⚡ Inicio Rápido (Opción Recomendada)

### 1. Requisitos Previos

- ✅ **Docker Desktop** (ya instalado)
- ✅ **Git** (para clonar el repositorio)
- ✅ **Windows 10/11** con PowerShell

### 2. Despliegue Automático

Tenemos **dos opciones** para facilitar el despliegue:

#### Opción A: Script Interactivo (Más Fácil)

```batch
# Ejecuta el administrador de despliegue
deploy-manager.bat
```

#### Opción B: Script PowerShell (Más Control)

```powershell
# Despliegue completo de desarrollo con datos de prueba
.\deploy.ps1 -Environment dev -Seed

# O si quieres limpiar todo y empezar desde cero
.\deploy.ps1 -Environment dev -Clean -Reset
```

### 3. ¿Qué hace el script automáticamente?

1. **Verifica prerrequisitos**: Docker, archivos de configuración
2. **Construye las imágenes**: Backend, PostgreSQL, Redis
3. **Inicia los servicios**: API en puerto 8000, DB en 5432
4. **Configura la base de datos**: Migraciones de Prisma
5. **Puebla datos iniciales**: Desde tu base de datos Neon
6. **Verifica funcionamiento**: Health checks automáticos

### 4. URLs Disponibles Después del Despliegue

| Servicio          | URL                          | Descripción                       |
| ----------------- | ---------------------------- | --------------------------------- |
| **API Principal** | http://localhost:8000        | Backend de SOPA                   |
| **Documentación** | http://localhost:8000/docs   | Swagger UI interactivo            |
| **Health Check**  | http://localhost:8000/health | Estado del servicio               |
| **PostgreSQL**    | localhost:5432               | Base de datos (usuario: postgres) |
| **Redis**         | localhost:6379               | Cache/Sessions                    |

## 🛠️ Comandos Útiles

### Gestión de Servicios

```bash
# Ver estado de todos los servicios
docker compose -f docker-compose.dev.yml ps

# Ver logs en tiempo real
docker compose -f docker-compose.dev.yml logs -f

# Parar todos los servicios
docker compose -f docker-compose.dev.yml down

# Reiniciar un servicio específico
docker compose -f docker-compose.dev.yml restart api
```

### Gestión de Base de Datos

```bash
# Acceder al contenedor de la API
docker exec -it sopa_api_dev bash

# Una vez dentro del contenedor:
python scripts/db_manager.py seed        # Poblar base de datos
python scripts/db_manager.py reset       # Resetear base de datos
python scripts/db_manager.py subjects    # Solo sincronizar subjects
python scripts/db_manager.py reset-seed  # Resetear y poblar
```

### Acceso Directo a Base de Datos

```bash
# Conectarse a PostgreSQL directamente
docker exec -it sopa_postgres_dev psql -U postgres -d sopa_dev
```

## 🎯 Verificación Rápida

Después del despliegue, verifica que todo funcione:

```bash
# 1. Verificar API
curl http://localhost:8000/health

# 2. Ver documentación en el navegador
start http://localhost:8000/docs

# 3. Verificar base de datos
docker exec sopa_postgres_dev pg_isready -U postgres
```

## 📊 Estructura del Proyecto

```
SOPA-BACKEND/
├── deploy.ps1              # Script de despliegue PowerShell
├── deploy-manager.bat      # Interface interactiva
├── docker-compose.dev.yml  # Configuración desarrollo
├── docker-compose.prod.yml # Configuración producción
├── .env.dev               # Variables de entorno desarrollo
├── Dockerfile             # Imagen del backend
├── src/                   # Código fuente
│   ├── main.py           # FastAPI application
│   └── modules/          # Módulos del API
├── prisma/               # Base de datos
│   └── schema.prisma     # Esquema de la BD
└── scripts/              # Scripts de utilidad
    ├── db_manager.py     # Gestor de base de datos
    └── sync_subjects.py  # Sincronización con Neon
```

## 🔧 Solución de Problemas Comunes

### 1. Error: "Docker no está ejecutándose"

```bash
# Iniciar Docker Desktop manualmente
# O reiniciar el servicio de Docker
```

### 2. Error: "Puerto 8000 ya en uso"

```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr :8000

# Terminar proceso si es necesario o cambiar puerto en docker-compose.dev.yml
```

### 3. Error en migraciones de Prisma

```bash
# Regenerar cliente de Prisma
docker exec sopa_api_dev prisma generate

# Aplicar migraciones forzadamente
docker exec sopa_api_dev prisma migrate deploy
```

### 4. Base de datos vacía

```bash
# Repoblar base de datos
docker exec sopa_api_dev python scripts/db_manager.py reset-seed
```

## 🎉 ¡Ya está listo!

Si todo salió bien, deberías tener:

- ✅ API funcionando en http://localhost:8000
- ✅ Base de datos PostgreSQL con datos sincronizados
- ✅ Redis para cache
- ✅ Documentación interactiva en /docs

## 📞 Ayuda Adicional

- **Logs detallados**: Usa `deploy-manager.bat` → opción 7
- **Estado de servicios**: Usa `deploy-manager.bat` → opción 8
- **Guía completa**: Ver `DEPLOYMENT_GUIDE.md`

---

**¡Happy Coding! 🚀**
