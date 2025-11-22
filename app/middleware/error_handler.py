from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.logger_config import get_logger

log = get_logger()


def register_exception_handlers(app):
    """
    Registra tratadores de exceções globais no app FastAPI.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log.warning(
            f"HTTPException: {exc.detail} (status={exc.status_code}) - Path: {request.url}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        log.error(f"Erro de validação: {exc.errors()} - Path: {request.url}")
        return JSONResponse(
            status_code=422,
            content={"error": "Erro de validação nos dados", "details": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        log.exception(f"Erro inesperado: {exc} - Path: {request.url}")
        return JSONResponse(
            status_code=500,
            content={"error": "Ocorreu um erro interno no servidor"},
        )
