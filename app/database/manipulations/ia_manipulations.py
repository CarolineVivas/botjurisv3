from ..models import *
from ..connection import SessionLocal


def filter_ia(phone:str) -> IA:
    db = SessionLocal()

    if not db:
        raise(Exception("Não consegui conectar com databse"))
    
    try:
        ia = db.query(IA).filter(IA.phone_number == phone).first()
        if not ia:
            print(f"Nenhuma IA cadastrada com esse número de telefone {phone}")
            return None

        # Adicionar as Fks
        ia.ia_config
        ia.active_prompts

        print(f"IA localizada: {ia.name} - {ia.phone_number}")
        return ia

    except Exception as ex:
        print(f"Error : {ex}")

    finally:
        db.close()