# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "BotJuris"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str | None = None

    # 🔹 Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # 🔹 Segurança e API
    HOST_API: str | None = "http://127.0.0.1:8080"
    OPENAI_API_KEY: str | None = None
    FERNET_KEY: str | None = None
    WEBHOOK_SECRET: str | None = None

    class Config:
        env_file_encoding = "utf-8"
