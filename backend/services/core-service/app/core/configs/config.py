from functools import lru_cache
from pathlib import Path
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_DIALECT: str = "postgresql+psycopg2"
    DATABASE_HOSTNAME: str = "postgres_container"
    DATABASE_NAME: str = "shopify"
    DATABASE_PASSWORD: str = "admin"
    DATABASE_PORT: int = 5432
    DATABASE_USERNAME: str = "postgres"
    DEBUG_MODE: bool = False
    # REDIS_URL: str = "localhost"
    REDIS_URL: str = "redis"
    IAM_URL: str = "https://iam-tradehub.liara.run"
    REDIS_PORT: int = 6379
    JWT_SECRET_KEY : str = "3ffdda4a51a141cff4485a36f9cd137287f2526c1edb8300cd678ab96a49d1bd"
    JWT_ALGORITHM : str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OTP_EXPIRE_TIME: int = 3600
    # DATABASE_URL: str =  "7" 
    # MEDIA_URL: str = "http://127.0.0.1:8004"

@logger.catch
def get_settings():
    return Settings()