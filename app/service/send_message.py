import requests
from app.core.logger_config import get_logger

log = get_logger()


def enviar_mensagem(apikey: str, numero_destino: str, mensagem: str):
    """
    Envia mensagem de texto usando a API da Evolution.
    """
    url = "https://api.evolution.com/send-message"  # Substitua se for outro endpoint real da Evolution

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "apikey": apikey,
        "number": numero_destino,
        "text": mensagem
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        log.info(f"Mensagem enviada para {numero_destino}")
    except requests.exceptions.RequestException as e:
        log.error(f"Erro ao enviar mensagem: {e}")
