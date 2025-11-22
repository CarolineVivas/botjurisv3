"""
Dependencies para FastAPI - Dependency Injection.

Fornece funções que podem ser injetadas via Depends() do FastAPI,
seguindo princípios de Inversion of Control e facilitando testes.
"""

from typing import Generator

from sqlalchemy.orm import Session

from app.core.cache import CacheService, get_cache
from app.core.logger_config import get_logger
from app.database.connection import SessionLocal
from app.database.repositories import IARepository, LeadRepository

log = get_logger()


def get_db() -> Generator[Session, None, None]:
    """
    Fornece uma sessão do banco de dados com gerenciamento automático.

    Yields:
        Session: Sessão SQLAlchemy

    Note:
        - Faz commit automático se não houver exceções
        - Faz rollback automático em caso de exceção
        - Sempre fecha a sessão ao final

    Usage:
        ```python
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            # usa db
            pass
        ```
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as ex:
        log.error(f"Erro na transação do banco de dados: {ex}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def get_ia_repository(db: Session = None) -> IARepository:
    """
    Fornece um IARepository.

    Args:
        db: Sessão do banco (injetada automaticamente via Depends)

    Returns:
        IARepository: Repository para operações com IA

    Usage:
        ```python
        def process_ia(
            ia_repo: IARepository = Depends(get_ia_repository)
        ):
            ia = ia_repo.get_by_phone("...")
        ```
    """
    if db is None:
        # Para uso fora do FastAPI (workers, etc)
        db = SessionLocal()

    return IARepository(db)


def get_lead_repository(db: Session = None) -> LeadRepository:
    """
    Fornece um LeadRepository.

    Args:
        db: Sessão do banco (injetada automaticamente via Depends)

    Returns:
        LeadRepository: Repository para operações com Lead

    Usage:
        ```python
        def process_lead(
            lead_repo: LeadRepository = Depends(get_lead_repository)
        ):
            lead = lead_repo.get_by_phone("...")
        ```
    """
    if db is None:
        # Para uso fora do FastAPI (workers, etc)
        db = SessionLocal()

    return LeadRepository(db)


def get_cache_service() -> CacheService:
    """
    Fornece uma instância do CacheService.

    Returns:
        CacheService: Serviço de cache Redis

    Usage:
        ```python
        def my_endpoint(
            cache: CacheService = Depends(get_cache_service)
        ):
            cache.set("key", "value", ttl=300)
        ```
    """
    return get_cache()
