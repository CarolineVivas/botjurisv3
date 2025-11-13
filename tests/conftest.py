# tests/conftest.py

import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import Settings

# Opcional: garantir que usamos um .env de teste
os.environ.setdefault("ENV", "test")


@pytest.fixture(scope="session")
def settings() -> Settings:
    """
    Configurações da aplicação em ambiente de testes.
    Se você tiver um .env.test, pode apontar aqui.
    """
    env_file = ".env.test" if os.path.exists(".env.test") else ".env.dev"
    return Settings(_env_file=env_file)


@pytest.fixture(scope="session")
def client(settings: Settings) -> TestClient:
    """
    Cliente HTTP para testar a API (FastAPI TestClient).
    """
    return TestClient(app)


@pytest.fixture
def db_session():
    """
    Sessão de banco para testes.
    Idealmente, use um banco separado só para teste.
    """
    try:
        from app.database import get_session
    except ImportError:
        pytest.skip("get_session não encontrado em app.database")

    session = get_session()
    try:
        yield session
    finally:
        session.close()
