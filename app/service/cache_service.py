from app.core.cache import redis_client
import json
from typing import Optional

CACHE_EXPIRATION = 3600  # ⏱️ 1 hora padrão


# ============================================================
# 🔹 Funções genéricas
# ============================================================
def set_cache(key: str, value: dict, expire_seconds: int = CACHE_EXPIRATION) -> None:
    """Armazena um dicionário no cache Redis."""
    if not redis_client:
        return
    try:
        redis_client.setex(key, expire_seconds, json.dumps(value))
    except Exception as e:
        print(f"⚠️ Erro ao salvar no cache ({key}): {e}")


def get_cache(key: str) -> Optional[dict]:
    """Recupera e desserializa um valor do cache Redis."""
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"⚠️ Erro ao ler do cache ({key}): {e}")
        return None


def delete_cache(key: str) -> None:
    """Remove uma chave específica do cache."""
    if not redis_client:
        return
    try:
        redis_client.delete(key)
    except Exception as e:
        print(f"⚠️ Erro ao deletar chave do cache ({key}): {e}")


def clear_all_cache() -> None:
    """⚠️ Apaga todo o cache (use com cautela)."""
    if not redis_client:
        return
    try:
        redis_client.flushall()
        print("🧹 Cache limpo com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao limpar cache: {e}")


# ============================================================
# 🔹 Prompts ativos
# ============================================================
def cache_prompt(prompt_id: str, prompt_data: dict, ttl: int = 3600):
    """Armazena um prompt ativo no cache (1h padrão)."""
    set_cache(f"prompt:{prompt_id}", prompt_data, expire_seconds=ttl)


def get_cached_prompt(prompt_id: str):
    """Recupera prompt ativo do cache, se existir."""
    return get_cache(f"prompt:{prompt_id}")


# ============================================================
# 🔹 Configurações da IA
# ============================================================
def cache_ia_config(config_data: dict, ttl: int = 7200):
    """Guarda as configurações atuais da IA (modelo, prompt, etc)."""
    set_cache("ia:config", config_data, expire_seconds=ttl)


def get_cached_ia_config():
    """Recupera configuração atual da IA, se existir."""
    return get_cache("ia:config")


# ============================================================
# 🔹 Sessões de Leads
# ============================================================
def cache_lead_session(lead_id: str, session_data: dict, ttl: int = 1800):
    """Armazena sessão ativa do lead (30 minutos padrão)."""
    set_cache(f"lead_session:{lead_id}", session_data, expire_seconds=ttl)


def get_lead_session(lead_id: str):
    """Recupera sessão ativa do lead, se existir."""
    return get_cache(f"lead_session:{lead_id}")
