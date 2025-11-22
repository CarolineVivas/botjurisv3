"""
Templates de mensagens da aplicação.

Centraliza mensagens pré-definidas usadas no sistema,
facilitando tradução e personalização.
"""

from typing import List


class MessageTemplates:
    """Templates de mensagens do sistema."""

    # Mensagens exibidas antes de enviar listas longas
    PRE_LIST_MESSAGES: List[str] = [
        "Um minutinho que irei te passar as informações",
        "Só um instante, vou buscar as informações para você",
        "Aguarde um pouquinho, estou reunindo os dados",
        "Um momento, logo trago os detalhes",
        "Espere só um instante enquanto preparo as informações",
        "Dá só um minuto, já estou organizando os dados para você",
        "Só um segundinho, já te passo as informações",
        "Por favor, aguarde um instante que estou separando os dados",
        "Um pouquinho de paciência, estou juntando os detalhes",
        "Aguarde um momento, estou coletando as informações",
        "Só mais um instante, estou preparando tudo para você",
        "Um instante, vou te mostrar as informações",
        "Dê-me um momento, estou buscando os dados necessários",
        "Aguarde só um minutinho, logo te passo os detalhes",
        "Só um momento, estou reunindo todos os dados",
        "Um segundinho, estou organizando as informações",
        "Aguarde um pouquinho, estou finalizando os detalhes",
        "Só um instante, já tenho as informações para você",
        "Dê-me um minutinho, estou juntando todas as informações",
        "Por favor, aguarde um momento enquanto preparo os dados",
    ]

    # Configurações de quebra de mensagem
    MAX_MESSAGE_LENGTH = 4000
    MIN_LIST_ITEMS_FOR_PRE_MESSAGE = 3
    TYPING_SPEED_WPM = 75  # palavras por minuto
    MAX_TYPING_DELAY_SECONDS = 10
    TYPING_DELAY_MULTIPLIER = 30  # converte minutos para segundos

    # Configurações de memória da IA
    CONVERSATION_MEMORY_WINDOW = 20  # número de mensagens mantidas em memória
    RESUME_MEMORY_WINDOW = 60  # número de mensagens para resumo

    # Configurações de geração de resumo
    RESUME_INTERVAL_MIN = 20  # mínimo de interações para gerar resumo
    RESUME_INTERVAL_MAX = 25  # máximo de interações para gerar resumo
