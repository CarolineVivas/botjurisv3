import os
import redis
from dotenv import load_dotenv
from app.core.logger_config import get_logger

log = get_logger()
load_dotenv()

# 🔗 Lê variáveis do .env
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# 🔧 Inicializa o cliente global (como None)
redis_client = None


def init_cache():
    """
    Inicializa conexão com o Redis e faz ping.
    """
    global redis_client
    try:
        redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        log.info("Redis conectado com sucesso.")
    except Exception as e:
        log.error(f"Erro ao conectar ao Redis: {e}")
        redis_client = None


# 🚀 Inicializa automaticamente quando o módulo é importado
try:
    init_cache()
except Exception as e:
    log.warning(f"Falha ao inicializar Redis automaticamente: {e}")


# 🧹 Função genérica para limpar cache por prefixo
def invalidate_cache(prefix: str):
    """
    Remove todas as chaves Redis que começam com determinado prefixo.
    """
    global redis_client
    if not redis_client:
        log.warning("Redis não inicializado.")
        return

    try:
        keys = redis_client.keys(f"{prefix}:*")
        if not keys:
            log.info(f"Nenhuma chave encontrada com prefixo: {prefix}")
            return
        for key in keys:
            redis_client.delete(key)
        log.info(f"Cache limpo para prefixo: {prefix}")
    except Exception as e:
        log.error(f"Erro ao invalidar cache: {e}")

