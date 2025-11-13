import re
import unicodedata

# Remove caracteres de controle e normaliza acentuação
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")

def sanitize_text(text: str, max_len: int = 4000) -> str:
    """
    Limpa e normaliza o texto recebido, garantindo segurança e consistência.

    - Remove caracteres de controle invisíveis
    - Normaliza acentuação (NFKC)
    - Remove espaços duplos e quebras excessivas
    - Limita tamanho máximo (padrão: 4000 caracteres)
    """
    if not text:
        return ""

    # Normaliza acentuação e caracteres compostos (ex: ç, á)
    text = unicodedata.normalize("NFKC", text)

    # Remove caracteres de controle invisíveis
    text = _CONTROL_CHARS.sub("", text)

    # Substitui múltiplos espaços e quebras de linha
    text = re.sub(r"\s+", " ", text)

    # Remove espaços nas extremidades
    text = text.strip()

    # Limita tamanho máximo (protege contra flood)
    if len(text) > max_len:
        text = text[:max_len]

    return text


def sanitize_dict(data: dict, max_len: int = 4000) -> dict:
    """
    Aplica sanitização em todos os valores de um dicionário recursivamente.
    Ideal para limpar payloads de mensagens e respostas da IA.
    """
    if not isinstance(data, dict):
        return data

    clean_data = {}
    for key, value in data.items():
        if isinstance(value, str):
            clean_data[key] = sanitize_text(value, max_len=max_len)
        elif isinstance(value, dict):
            clean_data[key] = sanitize_dict(value, max_len=max_len)
        elif isinstance(value, list):
            clean_data[key] = [sanitize_text(v, max_len=max_len) if isinstance(v, str) else v for v in value]
        else:
            clean_data[key] = value
    return clean_data
