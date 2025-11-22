"""
Serviço de geração de respostas via LLM (Language Model).

Responsável por interagir com modelos de linguagem (OpenAI)
para gerar respostas e resumos de conversas.
"""

from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai.chat_models import ChatOpenAI
from langchain.chains.conversation.base import ConversationChain
from langchain.prompts import PromptTemplate

from app.service.cache_service import get_cache, set_cache
from app.config.prompts import PromptTemplates
from app.config.messages import MessageTemplates
from app.core.logger_config import get_logger

log = get_logger()


class LLMService:
    """
    Serviço simplificado para interação com LLM.

    Responsabilidades:
    - Gerar respostas de conversação
    - Gerar resumos de histórico
    - Gerenciar memória de conversação
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        resume: Optional[str] = None
    ):
        """
        Inicializa o serviço LLM.

        Args:
            api_key: Chave da API OpenAI
            model: Modelo a ser usado (ex: gpt-4o-mini)
            system_prompt: Prompt do sistema
            resume: Resumo prévio da conversa (opcional)
        """
        self.api_key = api_key
        self.model = model or "gpt-4o-mini"
        self.system_prompt = system_prompt
        self.resume = resume

    def generate_response(
        self,
        user_message: str,
        history: List[Dict[str, Any]] = None
    ) -> str:
        """
        Gera resposta da IA para mensagem do usuário.

        Args:
            user_message: Mensagem do usuário
            history: Histórico de mensagens (opcional)

        Returns:
            str: Resposta da IA

        Raises:
            ValueError: Se não conseguir gerar resposta
        """
        if history is None:
            history = []

        try:
            # Prepara prompt
            prompt_text = self._prepare_conversation_prompt()

            # Cria chain de conversação
            conversation = self._create_conversation_chain(
                prompt_text,
                MessageTemplates.CONVERSATION_MEMORY_WINDOW
            )

            # Alimenta memória com histórico
            self._feed_memory(conversation, history, user_message)

            # Gera resposta
            log.debug(f"Total de interações: {len(history)}")
            response = conversation.predict(input=user_message)
            log.info(f"Resposta IA gerada: {response[:100]}...")

            return response

        except Exception as ex:
            log.error(f"Erro ao processar resposta: {ex}", exc_info=True)
            return ""

    def generate_resume(
        self,
        history: List[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Gera resumo do histórico de conversação.

        Args:
            history: Histórico de mensagens

        Returns:
            Optional[str]: Resumo gerado ou None se falhar
        """
        if history is None:
            history = []

        try:
            # Cria chain específica para resumo
            conversation = self._create_conversation_chain(
                PromptTemplates.RESUME_GENERATION,
                MessageTemplates.RESUME_MEMORY_WINDOW
            )

            # Alimenta memória com histórico
            self._feed_memory(
                conversation,
                history,
                PromptTemplates.RESUME_REQUEST
            )

            # Gera resumo
            log.debug(f"Total de interações para resumo: {len(history)}")
            resume = conversation.predict(input=PromptTemplates.RESUME_REQUEST)
            log.info(f"Resumo IA gerado: {resume[:100]}...")

            return resume

        except Exception as ex:
            log.error(f"Erro ao processar resumo: {ex}", exc_info=True)
            return None

    def _prepare_conversation_prompt(self) -> str:
        """
        Prepara o prompt de conversação incluindo resumo se disponível.

        Returns:
            str: Template de prompt preparado
        """
        base_prompt = PromptTemplates.get_conversation_template(
            with_resume=bool(self.resume)
        )

        if self.resume:
            log.info("Resumo localizado, incluindo no contexto")
            # Adiciona resumo ao system prompt
            resume_context = f"\nresumo de todas as interações que teve com este lead: {self.resume}"
            return self.system_prompt + resume_context + "\n" + base_prompt

        return self.system_prompt + "\n" + base_prompt

    def _create_conversation_chain(
        self,
        prompt_template: str,
        memory_window: int
    ) -> ConversationChain:
        """
        Cria uma chain de conversação com LangChain.

        Args:
            prompt_template: Template do prompt
            memory_window: Janela de memória (número de mensagens)

        Returns:
            ConversationChain: Chain configurada
        """
        chat = ChatOpenAI(model=self.model, api_key=self.api_key)
        memory = ConversationBufferWindowMemory(k=memory_window)
        template = PromptTemplate.from_template(prompt_template)

        return ConversationChain(
            llm=chat,
            memory=memory,
            prompt=template
        )

    def _feed_memory(
        self,
        conversation: ConversationChain,
        history: List[Dict[str, Any]],
        current_message: str
    ) -> None:
        """
        Alimenta a memória da conversação com histórico.

        Args:
            conversation: Chain de conversação
            history: Histórico de mensagens
            current_message: Mensagem atual
        """
        if not history:
            conversation.memory.chat_memory.add_user_message(current_message)
            return

        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "user":
                conversation.memory.chat_memory.add_user_message(content)
            elif role == "assistant":
                conversation.memory.chat_memory.add_ai_message(content)


# ===============================================================
#  🔹 CLASSE LEGACY (compatibilidade com código antigo)
# ===============================================================
class IAresponse(LLMService):
    """
    Classe legacy mantida para compatibilidade.

    DEPRECATED: Use LLMService diretamente.
    """

    def __init__(self, api_key: str, ia_model: str, system_prompt: str, resume_lead: str = ""):
        """Construtor legacy."""
        super().__init__(api_key, ia_model, system_prompt, resume_lead or None)


def get_response_from_ai(user_message: str, user_id: str) -> str:
    """
    Função legacy para buscar resposta da IA com cache.

    DEPRECATED: Use LLMService diretamente com cache service.

    Args:
        user_message: Mensagem do usuário
        user_id: ID do usuário para cache

    Returns:
        str: Resposta da IA
    """
    from os import getenv

    cache_key = f"ia_response:{user_id}"

    # Tenta recuperar do cache
    cached = get_cache(cache_key)
    if cached:
        log.debug("Resposta carregada do cache")
        return cached["response"]

    # Gera nova resposta
    llm = LLMService(
        api_key=getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        system_prompt="Você é uma assistente jurídica do BotJuris."
    )

    response = llm.generate_response(user_message)

    # Armazena no cache
    set_cache(cache_key, {"response": response})

    return response
