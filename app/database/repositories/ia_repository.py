"""

Repository para gerenciamento de IAs no banco de dados.

"""

from typing import Optional

from sqlalchemy.orm import Session

from app.core.logger_config import get_logger
from app.database.models import IA

log = get_logger()


class IARepository:
    """

    Repository para operações relacionadas ao modelo IA.



    Encapsula toda a lógica de acesso a dados para IAs,

    seguindo o padrão Repository e facilitando testes.

    """

    def __init__(self, db: Session):
        """

        Inicializa o repository com uma sessão do banco.



        Args:

            db: Sessão SQLAlchemy injetada via dependency injection

        """

        self.db = db

    def get_by_phone(self, phone: str) -> Optional[IA]:
        """

        Busca IA por número de telefone.



        Args:

            phone: Número de telefone da IA



        Returns:

            Objeto IA se encontrado, None caso contrário

        """

        try:

            ia = self.db.query(IA).filter(IA.phone_number == phone).first()

            if not ia:

                log.warning(f"Nenhuma IA cadastrada com o número de telefone {phone}")

                return None

            # Eager loading das relações necessárias

            _ = ia.ia_config

            _ = ia.active_prompts

            log.info(f"IA localizada: {ia.name} - {ia.phone_number}")

            return ia

        except Exception as ex:

            log.error(f"Erro ao buscar IA por telefone {phone}: {ex}", exc_info=True)

            raise

    def get_by_id(self, ia_id: int) -> Optional[IA]:
        """

        Busca IA por ID.



        Args:

            ia_id: ID da IA



        Returns:

            Objeto IA se encontrado, None caso contrário

        """

        try:

            ia = self.db.query(IA).filter(IA.id == ia_id).first()

            if not ia:

                log.warning(f"IA não encontrada com ID {ia_id}")

                return None

            # Eager loading das relações

            _ = ia.ia_config

            _ = ia.active_prompts

            return ia

        except Exception as ex:

            log.error(f"Erro ao buscar IA por ID {ia_id}: {ex}", exc_info=True)

            raise
