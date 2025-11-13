import openai

# Cole sua API key aqui
openai.api_key = "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"

try:
    response = openai.models.list()
    print("✅ API key válida! Modelos disponíveis:")
    for model in response.data:
        print(model.id)
except openai.error.AuthenticationError:
    print("❌ API key inválida ou expirada.")
except Exception as e:
    print(f"⚠️ Erro inesperado: {e}")
