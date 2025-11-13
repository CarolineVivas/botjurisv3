# app/routers/webhook.py
from fastapi import APIRouter, Request, status
from app.core.logger_config import get_logger
from app.service.queue_manager import enqueue_webhook
from app.schemas.response import WebhookResponseDTO, ErrorDTO

router = APIRouter()
log = get_logger()

@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    response_model=WebhookResponseDTO
)
async def receive_webhook(request: Request):
    """
    Recebe o payload do Evolution e o enfileira para processamento assíncrono.
    """
    try:
        payload = await request.json()
        job_id = enqueue_webhook(payload)
        if job_id:
            log.info(f"📬 Webhook enfileirado | job_id={job_id}")
            return WebhookResponseDTO(message="Webhook recebido e enfileirado", status="ok")
        else:
            log.warning("⚠️ Webhook ignorado (lock ou circuit breaker)")
            return WebhookResponseDTO(message="Webhook ignorado (em processamento ou sistema ocupado)", status="ok")
    except Exception as ex:
        log.exception(f"❌ Erro ao enfileirar webhook: {ex}")
        # responde com schema de erro; se preferir HTTPException, ok também
        return ErrorDTO(message="Erro interno no recebimento", status="error")


