import time

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_log = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        now = time.time()
        if client_ip not in self.request_log:
            self.request_log[client_ip] = []
        # Filtra requisições dentro da janela de tempo
        recent_requests = [
            t for t in self.request_log[client_ip] if t > now - self.window_seconds
        ]
        self.request_log[client_ip] = recent_requests

        if len(recent_requests) >= self.max_requests:
            from app.core.logger_config import get_logger

            logger = get_logger()
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests")

        self.request_log[client_ip].append(now)
        response = await call_next(request)
        return response
