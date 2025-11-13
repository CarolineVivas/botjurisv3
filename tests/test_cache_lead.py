from app.service.cache_service import cache_lead_session, get_lead_session

cache_lead_session("lead123", {"nome": "Caroline", "ultima_mensagem": "Quero agendar consultoria"})
lead = get_lead_session("lead123")

print("👤 Sessão do lead:", lead)
