from langchain.memory import ConversationBufferWindowMemory
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains.conversation.base import ConversationChain
from langchain.prompts import PromptTemplate
from app.service.cache_service import get_cache, set_cache
from app.core.logger_config import get_logger
from os import getenv
from dotenv import load_dotenv

# ✅ Carrega variáveis do arquivo .env
load_dotenv()
log = get_logger()


# ============================================================
# 🔹 Função principal: busca resposta da IA e usa cache
# ============================================================
def get_response_from_ai(user_message: str, user_id: str):
    """
    Busca resposta da IA. Caso já exista no cache, reutiliza.
    """
    cache_key = f"ia_response:{user_id}"

    # ✅ 1. Tenta recuperar do cache
    cached = get_cache(cache_key)
    if cached:
        log.debug("Resposta carregada do cache")
        return cached["response"]

    # 🚀 2. Caso não tenha cache, cria uma IA e gera nova resposta
    ia = IAresponse(
        api_key=getenv("OPENAI_API_KEY"),
        ia_model="gpt-4o-mini",
        system_prompt="Você é uma assistente jurídica do BotJuris."
    )

    response = ia.generate_response(user_message)

    # 💾 3. Armazena no cache
    set_cache(cache_key, {"response": response})

    return response


# ============================================================
# 🔹 Classe IAresponse: encapsula geração de respostas e resumos
# ============================================================
class IAresponse:
    def __init__(self, api_key: str, ia_model: str, system_prompt: str, resume_lead: str = ""):
        self.api_key = api_key
        self.ia_model = ia_model
        self.system_prompt = system_prompt

        if resume_lead:
            log.info("Resumo localizado")
            response_prompt = """
            histórico da conversa:
            {history}

            usuário: {input}
            """
            resume_lead += f"\nresumo de todas as interações que teve com este lead: {resume_lead}"
        else:
            response_prompt = """
            histórico da conversa:
            {history}

            usuário: {input}
            """

        self.system_prompt += response_prompt
        if not self.ia_model:
            self.ia_model = "gpt-4o-mini"

    # ============================================================
    # 🔸 Gera resposta da IA com histórico (modo conversacional)
    # ============================================================
    def generate_response(self, message_lead: str, history_message: list = []) -> str:
        try:
            chat = ChatOpenAI(model=self.ia_model, api_key=self.api_key)
            memory = ConversationBufferWindowMemory(k=20)
            review_template = PromptTemplate.from_template(self.system_prompt)

            conversation = ConversationChain(
                llm=chat,
                memory=memory,
                prompt=review_template
            )

            # Alimentar memória da IA com histórico
            if not history_message:
                conversation.memory.chat_memory.add_user_message(message_lead)
            else:
                for msg in history_message:
                    if msg["role"] == "user":
                        conversation.memory.chat_memory.add_user_message(msg.get("content") or "")
                    elif msg["role"] == "assistant":
                        conversation.memory.chat_memory.add_ai_message(msg.get("content") or "")

            log.debug(f"Total de interações: {len(history_message)}")
            resposta = conversation.predict(input=message_lead)
            log.info(f"Resposta IA: {resposta}")

            return resposta

        except Exception as ex:
            log.error(f"Erro ao processar resposta: {ex}", exc_info=True)
            return ""

    # ============================================================
    # 🔸 Gera resumo completo do histórico de conversas
    # ============================================================
    def generate_resume(self, history_message: list = []) -> str:
        try:
            message = "Gere um resumo detalhado dessa conversa"
            system_prompt = """
            Você é um assistente especializado em resumir conversas com leads. Seu objetivo é identificar, extrair e armazenar de forma clara todos os pontos-chave e informações importantes:

            1. **Identificação dos Pontos-Chave**: Extraia os tópicos principais da conversa, incluindo necessidades, interesses, objeções e próximos passos do lead.
            2. **Organização das Informações**: Estruture o resumo de maneira clara e organizada, facilitando a visualização dos dados mais relevantes.
            3. **Foco nas Informações Relevantes**: Certifique-se de que nenhuma informação importante seja omitida. Dados como informações de contato, dúvidas específicas e requisitos do lead devem ser destacados.
            4. **Clareza e Concisão**: O resumo deve ser conciso, mas detalhado o suficiente para fornecer um panorama completo da conversa.
            5. **Privacidade e Segurança**: Garanta que todas as informações sensíveis sejam tratadas com a devida confidencialidade.

            Histórico da conversa:
            {history}
            Usuário: {input}
            """

            chat = ChatOpenAI(model=self.ia_model, api_key=self.api_key)
            memory = ConversationBufferWindowMemory(k=60)
            review_template = PromptTemplate.from_template(system_prompt)
            conversation = ConversationChain(
                llm=chat,
                memory=memory,
                prompt=review_template
            )

            # Alimentar memória da IA com histórico
            if not history_message:
                conversation.memory.chat_memory.add_user_message(message)
            else:
                for msg in history_message:
                    if msg["role"] == "user":
                        conversation.memory.chat_memory.add_user_message(msg.get("content") or "")
                    elif msg["role"] == "assistant":
                        conversation.memory.chat_memory.add_ai_message(msg.get("content") or "")

            log.debug(f"Total de interações: {len(history_message)}")
            resposta = conversation.predict(input=message)
            log.info(f"Resumo IA: {resposta}")

            return resposta
        except Exception as ex:
            log.error(f"Erro ao processar resumo: {ex}", exc_info=True)
            return None
