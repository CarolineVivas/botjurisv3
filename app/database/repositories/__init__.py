"""
Repositories - implementações do padrão Repository para acesso a dados.
Centraliza toda a lógica de acesso ao banco de dados, seguindo o princípio de Single Responsibility e facilitando testes.
"""

from app.database.repositories.ia_repository import IARepository
from app.database.repositories.lead_repository import LeadRepository

__all__ = ["IARepository", "LeadRepository"]
