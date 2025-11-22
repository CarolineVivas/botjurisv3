"""

Repository para gerenciamento de Leads no banco de dados.

"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.logger_config import get_logger
from app.database.models import Lead

log = get_logger()


class LeadRepository:
    """

    Repository para operações relacionadas ao modelo Lead.



    Encapsula toda a lógica de acesso a dados para Leads,

    seguindo o padrão Repository e permitindo transações adequadas.

    """

    def __init__(self, db: Session):
        """

        Inicializa o repository com uma sessão do banco.



        Args:

            db: Sessão SQLAlchemy injetada via dependency injection

        """

        self.db = db

    def get_by_phone(self, phone: str) -> Optional[Lead]:
        """

        Busca lead por número de telefone.



        Args:

            phone: Número de telefone do lead



        Returns:

            Objeto Lead se encontrado, None caso contrário

        """

        try:

            lead = self.db.query(Lead).filter(Lead.phone == phone).first()

            if not lead:

                log.info(f"Lead não localizado com o telefone {phone}")

                return None

            log.info(f"Lead localizado: {lead.name} - {lead.phone}")

            return lead

        except Exception as ex:

            log.error(f"Erro ao buscar lead por telefone {phone}: {ex}", exc_info=True)

            raise

    def get_by_id(self, lead_id: int) -> Optional[Lead]:
        """

        Busca lead por ID.



        Args:

            lead_id: ID do lead



        Returns:

            Objeto Lead se encontrado, None caso contrário

        """

        try:

            lead = self.db.query(Lead).filter(Lead.id == lead_id).first()

            if not lead:

                log.warning(f"Lead não localizado com ID {lead_id}")

                return None

            return lead

        except Exception as ex:

            log.error(f"Erro ao buscar lead por ID {lead_id}: {ex}", exc_info=True)

            raise

    def create(
        self, ia_id: int, phone: str, name: str, message: List[Dict[str, Any]]
    ) -> Lead:
        """

        Cria um novo lead.



        Args:

            ia_id: ID da IA associada

            phone: Número de telefone do lead

            name: Nome do lead

            message: Lista inicial de mensagens



        Returns:

            Lead criado



        Note:

            Não faz commit. O commit deve ser feito pela camada superior

            para permitir transações apropriadas.

        """

        try:

            lead = Lead(ia_id=ia_id, phone=phone, name=name, message=message)

            self.db.add(lead)

            self.db.flush()  # Flush para obter o ID sem fazer commit

            log.info(
                f"Novo Lead criado: [id: {lead.id}, Nome: {lead.name}] "
                f"da IA {lead.ia_id}"
            )

            return lead

        except Exception as ex:

            log.error(f"Erro ao criar novo lead: {ex}", exc_info=True)

            raise

    def add_message(self, lead: Lead, message: Dict[str, Any]) -> None:
        """

        Adiciona mensagem ao histórico do lead.



        Args:

            lead: Objeto Lead

            message: Dicionário com a mensagem a ser adicionada



        Note:

            Não faz commit. O commit deve ser feito pela camada superior.

        """

        try:

            historico = lead.message or []

            historico.append(message)

            lead.message = historico

            self.db.flush()

            log.debug(f"Mensagem adicionada ao lead {lead.id}")

        except Exception as ex:

            log.error(
                f"Erro ao adicionar mensagem ao lead {lead.id}: {ex}", exc_info=True
            )

            raise

    def update_with_response(
        self, lead: Lead, response: Dict[str, Any], resume: Optional[str] = None
    ) -> None:
        """

        Atualiza lead com resposta da IA e opcionalmente com resumo.



        Args:

            lead: Objeto Lead

            response: Dicionário com a resposta da IA

            resume: Resumo da conversa (opcional)



        Note:

            Não faz commit. O commit deve ser feito pela camada superior.

        """

        try:

            # Atualiza resumo se fornecido

            if resume:

                lead.resume = resume

                log.debug(f"Resumo atualizado para lead {lead.id}")

            # Adiciona resposta ao histórico

            historico = lead.message or []

            historico.append(response)

            lead.message = historico

            self.db.flush()

            log.info(f"Lead {lead.id} ({lead.name}) atualizado com resposta da IA")

        except Exception as ex:

            log.error(
                f"Erro ao atualizar lead {lead.id} com resposta: {ex}", exc_info=True
            )

            raise
