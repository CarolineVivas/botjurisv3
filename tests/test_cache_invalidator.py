from app.service.cache_invalidator import (
    invalidate_after_ia_update,
    invalidate_lead_session,
    invalidate_all,
)

if __name__ == "__main__":
    print("🧠 Testando invalidação de cache...")

    invalidate_after_ia_update()
    invalidate_lead_session("42")
    invalidate_all()

