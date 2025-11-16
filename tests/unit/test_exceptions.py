# tests/unit/test_exceptions.py
"""
Testes para exceções customizadas.
"""
import pytest

from app.core.exceptions import (
    BotJurisException,
    CacheError,
    ConfigurationError,
    DatabaseError,
    ExternalAPIError,
    ValidationError,
)


class TestCustomExceptions:
    """Testes para exceções customizadas"""

    def test_base_exception_with_message(self):
        """Testa exceção base com mensagem"""
        exc = BotJurisException(detail="Erro genérico")

        assert str(exc) == "500: Erro genérico"  # ou apenas:
        assert exc.detail == "Erro genérico"  # ← Melhor opção
        assert exc.status_code == 500

    def test_base_exception_with_custom_status(self):
        """Testa exceção base com status customizado"""
        exc = BotJurisException(detail="Erro customizado", status_code=418)

        assert exc.status_code == 418

    def test_validation_error(self):
        """Testa ValidationError"""
        exc = ValidationError(detail="Dados inválidos")

        assert exc.status_code == 400
        assert "inválidos" in exc.detail

    def test_database_error(self):
        """Testa DatabaseError"""
        exc = DatabaseError(detail="Falha na conexão")

        assert exc.status_code == 500
        assert "conexão" in exc.detail

    def test_external_api_error(self):
        """Testa ExternalAPIError"""
        exc = ExternalAPIError(detail="Evolution API falhou")

        assert exc.status_code == 502
        assert "API" in exc.detail

    def test_cache_error(self):
        """Testa CacheError"""
        exc = CacheError(detail="Redis indisponível")

        assert exc.status_code == 500
        assert "Redis" in exc.detail

    def test_configuration_error(self):
        """Testa ConfigurationError"""
        exc = ConfigurationError(detail=".env incompleto")

        assert exc.status_code == 500
        assert ".env" in exc.detail

    def test_exception_can_be_raised_and_caught(self):
        """Testa que exceções podem ser lançadas e capturadas"""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError(detail="Teste de validação")

        assert exc_info.value.status_code == 400
        assert "validação" in str(exc_info.value)

    def test_exception_inheritance(self):
        """Testa herança de exceções"""
        exc = ValidationError(detail="Teste")

        assert isinstance(exc, BotJurisException)
        assert isinstance(exc, Exception)
