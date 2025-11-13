# app/database/queries.py
from sqlalchemy.orm import Session
from app.database.models import IA, Lead, Prompt
from sqlalchemy import select

def get_active_ias(db: Session, limit=20, offset=0):
    """Busca IAs ativas com paginação."""
    return db.execute(
        select(IA).where(IA.status.is_(True)).offset(offset).limit(limit)
    ).scalars().all()

def get_lead_by_phone(db: Session, phone: str):
    """Busca lead pelo telefone (com join para IA)."""
    return db.execute(
        select(Lead).join(IA).where(Lead.phone == phone)
    ).scalars().first()

def get_active_prompt(db: Session, ia_id: int):
    """Busca prompt ativo da IA específica."""
    return db.execute(
        select(Prompt).where(Prompt.ia_id == ia_id, Prompt.is_active.is_(True))
    ).scalars().first()
