# tests/test_database.py

import pytest


@pytest.mark.db
def test_database_connection(db_session):
    """
    Verifica se a conexão com o banco está funcionando.
    Usa SELECT 1, que é genérico.
    """
    try:
        from sqlalchemy import text
    except ImportError:
        pytest.skip("SQLAlchemy não está disponível para este teste.")

    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1
