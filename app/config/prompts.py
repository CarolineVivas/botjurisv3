"""
Templates de prompts para LLM.

Centraliza todos os prompts usados pela aplicação,
facilitando manutenção e customização.
"""


class PromptTemplates:
    """Templates de prompts para diferentes funcionalidades."""

    # Prompt para conversação normal
    CONVERSATION = """
histórico da conversa:
{history}

usuário: {input}
"""

    # Prompt para conversação com resumo
    CONVERSATION_WITH_RESUME = """
histórico da conversa:
{history}

usuário: {input}
"""

    # Prompt para geração de resumos
    RESUME_GENERATION = """
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

    # Mensagem padrão para solicitar resumo
    RESUME_REQUEST = "Gere um resumo detalhado dessa conversa"

    @staticmethod
    def get_conversation_template(with_resume: bool = False) -> str:
        """
        Retorna o template apropriado para conversação.

        Args:
            with_resume: Se True, retorna template com resumo

        Returns:
            str: Template de prompt
        """
        return (
            PromptTemplates.CONVERSATION_WITH_RESUME
            if with_resume
            else PromptTemplates.CONVERSATION
        )
