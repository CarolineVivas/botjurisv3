# app/core/config.py
from typing import Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações centralizadas da aplicação.
    Carrega variáveis do .env automaticamente.
    """
    
    # ============================================================
    # 🔹 Informações da Aplicação
    # ============================================================
    APP_NAME: str = Field(default="BotJuris", description="Nome da aplicação")
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Ambiente de execução"
    )
    DEBUG: bool = Field(default=False, description="Modo debug")
    
    # ============================================================
    # 🔹 Banco de Dados
    # ============================================================
    DATABASE_URL: str = Field(
        ...,  # obrigatório
        description="URL de conexão com PostgreSQL"
    )
    
    # ============================================================
    # 🔹 Redis (Cache e Queue)
    # ============================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL completa do Redis"
    )
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)
    REDIS_DB: int = Field(default=0, ge=0, le=15)
    REDIS_PASSWORD: str | None = Field(default=None)
    
    # ============================================================
    # 🔹 Evolution API
    # ============================================================
    EVOLUTION_HOST: str = Field(
        ...,
        description="URL base da Evolution API (com / no final)"
    )
    EVOLUTION_API_KEY: str = Field(
        ...,
        min_length=10,
        description="API Key da Evolution"
    )
    
    # ============================================================
    # 🔹 OpenAI
    # ============================================================
    OPENAI_API_KEY: str = Field(
        ...,
        min_length=20,
        description="API Key da OpenAI"
    )
    MODEL_DEFAULT: str = Field(
        default="gpt-4o-mini",
        description="Modelo padrão para conversas"
    )
    MODEL_ANALYZE_IMAGE: str = Field(
        default="gpt-4o",
        description="Modelo para análise de imagens"
    )
    
    # ============================================================
    # 🔹 Segurança
    # ============================================================
    FERNET_KEY: str = Field(
        ...,
        min_length=44,
        description="Chave Fernet para criptografia (44 chars base64)"
    )
    WEBHOOK_SECRET: str | None = Field(
        default=None,
        description="Secret para validar assinaturas de webhook"
    )
    
    # ============================================================
    # 🔹 Rate Limiting
    # ============================================================
    RATE_LIMIT_REQUESTS: int = Field(default=10, ge=1)
    RATE_LIMIT_WINDOW: int = Field(default=60, ge=1)
    
    # ============================================================
    # 🔹 Validadores
    # ============================================================
    @field_validator("EVOLUTION_HOST")
    @classmethod
    def validate_evolution_host(cls, v: str) -> str:
        """Garante que o host termina com /"""
        if not v.endswith("/"):
            return v + "/"
        return v
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Valida ambientes permitidos"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT deve ser um de: {allowed}")
        return v
    
    # ============================================================
    # 🔹 Configurações do Pydantic
    # ============================================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # ignora variáveis extras no .env
        validate_default=True
    )
    
    # ============================================================
    # 🔹 Helpers
    # ============================================================
    @property
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.ENVIRONMENT == "development"
    
    def get_redis_url_with_password(self) -> str:
        """Constrói URL do Redis com senha se existir"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return self.REDIS_URL


# ============================================================
# 🔹 Instância global (Singleton)
# ============================================================
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Retorna instância única das configurações.
    Usa pattern Singleton para evitar múltiplas leituras do .env.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings