"""
Protocols (interfaces) para definir contratos de serviços e repositories.

Usando typing.Protocol para definir interfaces sem herança, permitindo
duck typing e facilitando testes com mocks.
"""

from typing import Protocol, Optional, List, Dict, Any
from app.database.models import IA, Lead


class IARepositoryProtocol(Protocol):
    """Contrato para repositório de IA."""

    def get_by_phone(self, phone: str) -> Optional[IA]:
        """Busca IA por número de telefone."""
        ...

    def get_by_id(self, ia_id: int) -> Optional[IA]:
        """Busca IA por ID."""
        ...


class LeadRepositoryProtocol(Protocol):
    """Contrato para repositório de Lead."""

    def get_by_phone(self, phone: str) -> Optional[Lead]:
        """Busca lead por número de telefone."""
        ...

    def get_by_id(self, lead_id: int) -> Optional[Lead]:
        """Busca lead por ID."""
        ...

    def create(
        self,
        ia_id: int,
        phone: str,
        name: str,
        message: List[Dict[str, Any]]
    ) -> Lead:
        """Cria um novo lead."""
        ...

    def add_message(self, lead: Lead, message: Dict[str, Any]) -> None:
        """Adiciona mensagem ao histórico do lead."""
        ...

    def update_with_response(
        self,
        lead: Lead,
        response: Dict[str, Any],
        resume: Optional[str] = None
    ) -> None:
        """Atualiza lead com resposta da IA e opcionalmente com resumo."""
        ...


class CacheProtocol(Protocol):
    """Contrato para serviço de cache."""

    def get(self, key: str) -> Optional[dict]:
        """Recupera valor do cache."""
        ...

    def set(self, key: str, value: dict, ttl: int = 3600) -> None:
        """Armazena valor no cache."""
        ...

    def delete(self, key: str) -> None:
        """Remove chave do cache."""
        ...

    def invalidate_by_prefix(self, prefix: str) -> None:
        """Remove todas as chaves com determinado prefixo."""
        ...


class MessageSenderProtocol(Protocol):
    """Contrato para serviço de envio de mensagens."""

    def send(
        self,
        instance: str,
        phone: str,
        message: str,
        delay: int = 0
    ) -> None:
        """Envia mensagem para o número especificado."""
        ...
