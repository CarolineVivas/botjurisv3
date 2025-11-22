# app/tasks/webhook_processor.py
import time

from app.core.logger_config import get_logger
from app.service.process import process_webhook_data

log = get_logger()


def process_webhook_task(payload: dict) -> str:
    """
    Task executada no worker. O timeout é controlado pelo RQ via 'job_timeout'.
    """
    start = time.monotonic()
    try:
        log.info("🛠️ Iniciando processamento de webhook no worker")
        # aqui você reusa seu fluxo já existente
        process_webhook_data(payload)
        elapsed = time.monotonic() - start
        log.info(f"✅ Webhook processado em {elapsed:.2f}s")
        return "ok"
    except Exception as ex:
        elapsed = time.monotonic() - start
        log.exception(f"❌ Falha ao processar webhook ({elapsed:.2f}s): {ex}")
        # raise para RQ registrar a falha e aplicar retry
        raise
