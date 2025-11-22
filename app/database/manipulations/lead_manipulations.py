from ..models import *
from ..connection import init_db
from app.core.logger_config import get_logger

log = get_logger()


def filter_lead(phone: str, message: dict) -> Lead:
    db = init_db()
    if not db:
        raise(Exception("Não consegui conectar com database"))

    try:
        lead = db.query(Lead).filter(Lead.phone == phone).first()
        if not lead:
            log.info(f"Lead não localizado com esse telefone {phone}")
            return None

        historico = lead.message
        if not historico:
            historico = []

        historico.append(message)
        lead.message = historico

        db.commit()
        db.refresh(lead)
        log.info(f"Lead localizado e conversa atualizada: {lead.name} - {lead.phone}")

        return lead

    except Exception as ex:
        log.error(f"Erro ao filtrar lead: {ex}", exc_info=True)
    finally:
        db.close()

    return None

def update_lead(lead_id:int, message:list, resume:str) -> bool:
    db = init_db()
    if not db:
            raise(Exception("Não consegui conectar com database"))

    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            log.warning(f"Lead não localizado com esse ID {lead_id}")
            return None

        if resume:
            lead.resume = resume

        historico = lead.message
        if not historico:
            historico = []

        historico.append(message)
        lead.message = historico

        db.commit()
        db.refresh(lead)
        log.info(f"Lead localizado e conversa atualizada: {lead.name} - {lead.phone}")

        return True

    except Exception as ex:
        log.error(f"Erro ao atualizar lead: {ex}", exc_info=True)
    finally:
        db.close()

    return False   

def new_lead(ia_id:int, phone:str, name:str, message:list) -> Lead:
    db = init_db()
    if not db:
        raise(Exception("Não consegui conectar com database"))

    try:
        lead = Lead(
            ia_id=ia_id,
            phone=phone,
            name=name,
            message=message
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        log.info(f"Novo Lead [id: {lead.id}, Nome: {lead.name}] da IA {lead.ia_id} adicionado com sucesso!")

        return lead

    except Exception as ex:
        log.error(f"Erro ao criar novo lead: {ex}", exc_info=True)
    finally:
        db.close()

    return None