


from pydantic import BaseSettings
from prisma import Prisma
from slowapi import Limiter
from slowapi.util import get_remote_address

database = Prisma(auto_register=True)
async def get_database():
    yield database


class Settings(BaseSettings):
    PROJECT_NAME: str = "SOPA UdeA"
    ALLOWED_HOSTS: str = "http://localhost:3000"

settings = Settings()
limiter = Limiter(key_func=get_remote_address)
