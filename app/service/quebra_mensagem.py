"""
Serviço de quebra e formatação de mensagens.

Responsável por quebrar mensagens longas em partes menores,
preservando formatação e aplicando delay de digitação.
"""

import re
import random
from typing import List, Dict
from app.core.logger_config import get_logger
from app.config.messages import MessageTemplates

log = get_logger()


class MessageFormatter:
    """Formatador de mensagens com proteção de padrões especiais."""

    # Padrões regex para proteção
    PATTERNS = {
        'money': r'R\$\d{1,3}(?:\.\d{3})*,\d{2}',
        'phone': r'\(\d{2}\)\s*\d{4,5}-\d{4,5}',
        'special': r'([!?.]{2,})',
        'list_item': r'^\s*(\d+\.\s+|-\s+)',
    }

    def __init__(self):
        """Inicializa o formatador."""
        self.placeholders: Dict[str, str] = {}

    def protect_patterns(self, text: str) -> str:
        """
        Protege padrões especiais substituindo-os por placeholders.

        Args:
            text: Texto original

        Returns:
            str: Texto com placeholders
        """
        # Proteger valores monetários
        text = self._protect_pattern(text, 'VALOR', self.PATTERNS['money'])

        # Proteger telefones
        text = self._protect_pattern(text, 'TELEFONE', self.PATTERNS['phone'])

        # Proteger caracteres especiais
        text = self._protect_pattern(text, 'ESPECIAL', self.PATTERNS['special'])

        return text

    def restore_patterns(self, text: str) -> str:
        """
        Restaura os padrões protegidos.

        Args:
            text: Texto com placeholders

        Returns:
            str: Texto original restaurado
        """
        for placeholder, original in self.placeholders.items():
            text = text.replace(placeholder, original)

        return text

    def _protect_pattern(self, text: str, prefix: str, pattern: str) -> str:
        """
        Protege um padrão específico.

        Args:
            text: Texto original
            prefix: Prefixo do placeholder
            pattern: Regex pattern

        Returns:
            str: Texto com placeholders
        """
        matches = re.findall(pattern, text)

        for i, match in enumerate(matches):
            placeholder = f'<{prefix}_{i}>'
            self.placeholders[placeholder] = match
            text = text.replace(match, placeholder)

        return text

    @staticmethod
    def is_list_item(text: str) -> bool:
        """
        Verifica se o texto é um item de lista.

        Args:
            text: Texto a verificar

        Returns:
            bool: True se for item de lista
        """
        return bool(re.match(MessageFormatter.PATTERNS['list_item'], text.strip()))


class MessageSplitter:
    """Divide mensagens longas em partes menores."""

    def __init__(self, max_length: int = None):
        """
        Inicializa o divisor.

        Args:
            max_length: Tamanho máximo da mensagem (usa default do config se não especificado)
        """
        self.max_length = max_length or MessageTemplates.MAX_MESSAGE_LENGTH
        self.formatter = MessageFormatter()

    def split(self, text: str) -> List[str]:
        """
        Divide mensagem em partes menores.

        Args:
            text: Texto a ser dividido

        Returns:
            List[str]: Lista de mensagens divididas
        """
        try:
            # Proteger padrões especiais
            protected_text = self.formatter.protect_patterns(text)

            # Dividir texto
            lines = protected_text.split('\n')
            messages = []

            # Processar baseado em se há listas ou não
            has_lists = any(self.formatter.is_list_item(line) for line in lines)

            if has_lists:
                messages = self._process_with_lists(lines)
            else:
                messages = self._process_simple(protected_text)

            # Restaurar padrões protegidos
            messages = [
                self.formatter.restore_patterns(msg)
                for msg in messages
                if msg.strip()
            ]

            # Processar listas Markdown (adicionar mensagem antes de listas longas)
            messages = self._process_markdown_lists(messages)

            log.debug(f"Mensagem quebrada em {len(messages)} partes")

            return messages

        except Exception as ex:
            log.error(f"Erro ao quebrar mensagem: {ex}", exc_info=True)
            return [text]  # Retorna texto original em caso de erro

    def _process_with_lists(self, lines: List[str]) -> List[str]:
        """
        Processa texto contendo listas.

        Args:
            lines: Linhas do texto

        Returns:
            List[str]: Mensagens processadas
        """
        messages = []
        current_message = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if self.formatter.is_list_item(line):
                # Salvar mensagem atual se existir
                if current_message:
                    messages.append(current_message.strip())
                    current_message = ""

                # Adicionar item da lista como mensagem separada
                messages.append(line)
            else:
                current_message += line + " "

        # Adicionar mensagem final se existir
        if current_message:
            messages.append(current_message.strip())

        return messages

    def _process_simple(self, text: str) -> List[str]:
        """
        Processa texto simples (sem listas).

        Args:
            text: Texto a processar

        Returns:
            List[str]: Mensagens processadas
        """
        # Dividir por sentenças simples (pontuação)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        messages = []
        current_message = ""

        for sentence in sentences:
            # Se adicionar essa sentença ultrapassar o limite, salvar mensagem atual
            if len(current_message) + len(sentence) > self.max_length and current_message:
                messages.append(current_message.strip())
                current_message = ""

            current_message += sentence + " "

        # Adicionar mensagem final
        if current_message:
            messages.append(current_message.strip())

        return messages

    def _process_markdown_lists(self, messages: List[str]) -> List[str]:
        """
        Processa listas Markdown, adicionando mensagem antes de listas longas.

        Args:
            messages: Mensagens originais

        Returns:
            List[str]: Mensagens processadas com avisos de lista
        """
        result = []
        i = 0

        while i < len(messages):
            if self.formatter.is_list_item(messages[i]):
                # Coletar todos os itens consecutivos da lista
                list_items = [messages[i]]
                j = i + 1

                while j < len(messages) and self.formatter.is_list_item(messages[j]):
                    list_items.append(messages[j])
                    j += 1

                # Se lista tem mais de 3 itens, adicionar mensagem de aviso
                if len(list_items) > MessageTemplates.MIN_LIST_ITEMS_FOR_PRE_MESSAGE:
                    pre_message = random.choice(MessageTemplates.PRE_LIST_MESSAGES)
                    result.append(pre_message)

                # Concatenar itens da lista
                combined = "\n".join(list_items).replace("**", "*")
                result.append(combined)

                i = j
            else:
                result.append(messages[i])
                i += 1

        return result


# ===============================================================
#  🔹 FUNÇÕES PÚBLICAS
# ===============================================================

def calculate_typing_delay(message: str) -> int:
    """
    Calcula delay de digitação baseado no tamanho da mensagem.

    Args:
        message: Mensagem a ser enviada

    Returns:
        int: Delay em segundos (máximo 10s)
    """
    try:
        words = len(message.split())
        typing_time = words / MessageTemplates.TYPING_SPEED_WPM  # minutos
        typing_time_seconds = typing_time * MessageTemplates.TYPING_DELAY_MULTIPLIER

        typing_time_seconds = round(typing_time_seconds)

        # Limitar ao máximo configurado
        if typing_time_seconds > MessageTemplates.MAX_TYPING_DELAY_SECONDS:
            typing_time_seconds = MessageTemplates.MAX_TYPING_DELAY_SECONDS

        return typing_time_seconds

    except Exception as ex:
        log.error(f"Erro ao calcular delay de digitação: {ex}", exc_info=True)
        return MessageTemplates.MAX_TYPING_DELAY_SECONDS


def quebrar_mensagens(
    texto: str,
    max_length: int = None
) -> List[str]:
    """
    Função principal para quebrar mensagens longas.

    Args:
        texto: Texto completo a ser segmentado
        max_length: Tamanho máximo da mensagem (opcional)

    Returns:
        List[str]: Lista de mensagens segmentadas
    """
    splitter = MessageSplitter(max_length)
    return splitter.split(texto)
