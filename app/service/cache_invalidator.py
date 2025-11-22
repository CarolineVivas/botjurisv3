from app.core.cache import invalidate_cache
from app.core.logger_config import get_logger

log = get_logger()


# 🧠 Limpa cache de prompts e IA
def invalidate_after_ia_update():
    try:
        invalidate_cache("ia_response")
        invalidate_cache("prompt")
        invalidate_cache("ia:config")
        log.info("🧠 Cache da IA e prompts invalidado.")
    except Exception as e:
        log.error(f"Erro ao invalidar cache de IA: {e}")


# 👤 Limpa cache da sessão de um lead específico
def invalidate_lead_session(lead_id: str):
    try:
        invalidate_cache(f"lead_session:{lead_id}")
        log.info(f"👤 Cache da sessão do lead {lead_id} foi limpo.")
    except Exception as e:
        log.error(f"Erro ao limpar cache de lead {lead_id}: {e}")


# 🧹 Limpa tudo (uso interno / manutenção)
def invalidate_all():
    try:
        invalidate_cache("")  # limpa todas as chaves
        log.info("🧹 Cache global da aplicação limpo.")
    except Exception as e:
        log.error(f"Erro ao limpar cache global: {e}")
