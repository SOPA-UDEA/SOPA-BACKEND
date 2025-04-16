from pydantic_settings import BaseSettings

# from prisma import Prisma
from slowapi import Limiter
from slowapi.util import get_remote_address

# database = Prisma(auto_register=True)


# async def get_database():
#     yield database


class Settings(BaseSettings):
    PROJECT_NAME: str = "SAM-GOV API"
    ALLOWED_HOSTS: str 
    SECRETS_PATH: str = "../secrets/keys.json"
    # SECRETS_PATH: str = "../secrets/ket_for_test.json"
    SAVE_FOLDER_PATH: str = "../session_save"
    SAM_API_ENDPOINT: str = "https://api.sam.gov/opportunities/v2/search"
    # DATABASE
    DATABASE_URL: str
    class Config:
        env_file = ".env"


settings = Settings()
limiter = Limiter(key_func=get_remote_address)
