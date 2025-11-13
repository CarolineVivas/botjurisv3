from app.service.cache_service import set_cache, get_cache, delete_cache

# 1️⃣ Grava um valor no cache
set_cache("teste:chave", {"mensagem": "Olá, Carol!"})

# 2️⃣ Lê o valor salvo
valor = get_cache("teste:chave")
print("📦 Valor no cache:", valor)

# 3️⃣ Remove o valor
delete_cache("teste:chave")
print("🧹 Chave removida.")

# 4️⃣ Confirma que foi apagado
valor_depois = get_cache("teste:chave")
print("🔍 Após deleção:", valor_depois)
