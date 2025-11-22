import os
from typing import List, Optional

import redis
from dotenv import load_dotenv

from app.core.logger_config import get_logger

log = get_logger()
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class CacheService:
    """Serviço de cache Redis com dependency injection."""

    def __init__(self, redis_url: str = REDIS_URL):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> Optional[redis.Redis]:
        """Lazy connection - conecta apenas quando necessário."""
        if self._client is None:
            self._connect()
        return self._client

    def _connect(self) -> None:
        """Conecta ao Redis."""
        try:
            self._client = redis.StrictRedis.from_url(
                self.redis_url, decode_responses=True
            )
            self._client.ping()
            log.info("Redis conectado com sucesso.")
        except Exception as e:
            log.error(f"Erro ao conectar ao Redis: {e}")
            self._client = None

    def invalidate_cache(self, prefix: str) -> None:
        """Remove todas as chaves que começam com o prefixo."""
        if not self.client:
            log.warning("Redis não inicializado.")
            return

        try:
            keys: List[str] = self.client.keys(f"{prefix}:*")
            if not keys:
                log.info(f"Nenhuma chave encontrada com prefixo: {prefix}")
                return

            for key in keys:
                self.client.delete(key)
            log.info(f"Cache limpo para prefixo: {prefix} ({len(keys)} chaves)")
        except Exception as e:
            log.error(f"Erro ao invalidar cache: {e}")

    def get(self, key: str) -> Optional[str]:
        """Obtém valor do cache."""
        if not self.client:
            return None
        try:
            return self.client.get(key)
        except Exception as e:
            log.error(f"Erro ao obter chave {key}: {e}")
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Define valor no cache com TTL opcional (em segundos)."""
        if not self.client:
            return False
        try:
            if ttl:
                self.client.setex(key, ttl, value)
            else:
                self.client.set(key, value)
            return True
        except Exception as e:
            log.error(f"Erro ao definir chave {key}: {e}")
            return False


# Singleton global para compatibilidade com código legado
_cache_instance: Optional[CacheService] = None


def get_cache() -> CacheService:
    """Retorna instância singleton do cache."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance


# Funções legadas para compatibilidade
def init_cache() -> None:
    """Inicializa cache (mantido para compatibilidade)."""
    get_cache()


def invalidate_cache(prefix: str) -> None:
    """Remove cache por prefixo (mantido para compatibilidade)."""
    get_cache().invalidate_cache(prefix)
