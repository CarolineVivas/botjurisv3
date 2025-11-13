from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.logger_config import get_logger

logger = get_logger()

async def error_handler(request: Request, call_next):
    """Middleware global para capturar exceções"""
    try:
        response = await call_next(request)
        return response
    except Exception as ex:
        logger.exception(f"Erro durante a requisição: {ex}")
        return JSONResponse(
            status_code=500,
            content={"message": "Erro interno do servidor", "details": str(ex)},
        )
