from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

CDN_ALLOW = "https://cdn.jsdelivr.net https://unpkg.com"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Cabeçalhos comuns
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Server"] = "BotJurisSecure"

        path = request.url.path

        # 👉 Exceção: Swagger UI e OpenAPI precisam carregar JS/CSS do CDN
        if path.startswith("/docs") or path == "/openapi.json":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                f"script-src 'self' 'unsafe-inline' 'unsafe-eval' {CDN_ALLOW}; "
                f"style-src 'self' 'unsafe-inline' {CDN_ALLOW}; "
                f"img-src 'self' data: blob: {CDN_ALLOW}; "
                "font-src 'self' data:; "
            )
        else:
            # CSP mais rígido para o resto do app
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob:; "
                "font-src 'self' data:; "
            )

        return response
