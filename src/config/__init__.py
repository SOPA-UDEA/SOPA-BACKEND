from pydantic_settings import BaseSettings

# from prisma import Prisma
from slowapi import Limiter
from slowapi.util import get_remote_address

# database = Prisma(auto_register=True)


# async def get_database():
#     yield database


class Settings(BaseSettings):
    PROJECT_NAME: str = "SOPA API"
    ALLOWED_HOSTS: str
    SECRETS_PATH: str = "../secrets/keys.json"
    # SECRETS_PATH: str = "../secrets/ket_for_test.json"
    SAVE_FOLDER_PATH: str = "../session_save"
    SAM_API_ENDPOINT: str = "https://api.sam.gov/opportunities/v2/search"
    # DATABASE
    DATABASE_URL: str
    NEON_DATABASE_URL: str = ""  # Optional for seeding from cloud database

    # Variables de entorno adicionales (opcionales para Docker)
    POSTGRES_DB: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "debug"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Permite variables extra sin causar errores


settings = Settings()
limiter = Limiter(key_func=get_remote_address)
