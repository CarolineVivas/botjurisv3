from app.service.cache_service import cache_ia_config, get_cached_ia_config

cache_ia_config({"modelo": "gpt-4o-mini", "contexto": "assistente jurídica"})
config = get_cached_ia_config()

print("🧠 Configuração armazenada:", config)
