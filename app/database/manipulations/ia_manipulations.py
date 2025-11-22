from typing import Optional

from app.core.logger_config import get_logger

from ..connection import SessionLocal
from ..models import IA

log = get_logger()


def filter_ia(phone: str) -> Optional[IA]:
    db = SessionLocal()

    if not db:
        raise (Exception("Não consegui conectar com databse"))

    try:
        ia = db.query(IA).filter(IA.phone_number == phone).first()
        if not ia:
            log.warning(f"Nenhuma IA cadastrada com esse número de telefone {phone}")
            return None

        # Adicionar as Fks
        ia.ia_config
        ia.active_prompts

        log.info(f"IA localizada: {ia.name} - {ia.phone_number}")
        return ia

    except Exception as ex:
        log.error(f"Erro ao filtrar IA: {ex}", exc_info=True)
        return None
    finally:
        db.close()
