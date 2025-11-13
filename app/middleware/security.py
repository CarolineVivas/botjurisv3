import hmac
import hashlib
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger_config import get_logger
import os

log = get_logger()

class SignatureValidationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.secret = "chave_super_segura_gerada_no_painel"  # ✅ segredo da Evolution

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/webhook":
            signature = request.headers.get("X-Signature")
            if not signature:
                raise HTTPException(status_code=401, detail="Missing signature header")

            body = await request.body()
            computed_signature = hmac.new(
                self.secret.encode(),
                body,
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(computed_signature, signature):
                log.warning("🚫 Assinatura do webhook inválida")
                raise HTTPException(status_code=403, detail="Invalid webhook signature")

        response = await call_next(request)
        return response
