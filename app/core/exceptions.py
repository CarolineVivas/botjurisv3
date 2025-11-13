from fastapi import HTTPException

class AppBaseException(HTTPException):
    """Exceção base customizada."""
    def __init__(self, status_code=400, detail="Erro interno"):
        super().__init__(status_code=status_code, detail=detail)

class ExternalAPIError(AppBaseException):
    """Erro de integração com APIs externas"""
    def __init__(self, detail="Erro na comunicação com API externa"):
        super().__init__(status_code=502, detail=detail)

class ValidationError(AppBaseException):
    """Erro de validação de dados"""
    def __init__(self, detail="Dados inválidos"):
        super().__init__(status_code=422, detail=detail)
