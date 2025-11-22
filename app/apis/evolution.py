# app/apis/evolution.py
import base64
import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv
from pydub import AudioSegment

from app.core.exceptions import ExternalAPIError
from app.core.logger_config import get_logger

load_dotenv()
log = get_logger()

# Configurações centralizadas
EVOLUTION_HOST = os.getenv("EVOLUTION_HOST")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ANALYZE_IMAGE = os.getenv("MODEL_ANALYZE_IMAGE_OPENAI", "gpt-4o")

if not EVOLUTION_HOST or not EVOLUTION_API_KEY:
    raise ValueError("⚠️ EVOLUTION_HOST e EVOLUTION_API_KEY devem estar no .env")


class EvolutionAPIError(ExternalAPIError):
    """Exceção específica para erros da Evolution API"""

    pass


def _make_request(
    url: str,
    body: Dict[str, Any],
    max_retries: int = 3,
    wait_seconds: int = 2,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Faz requisição POST para Evolution API com retry automático.

    Args:
        url: URL completa do endpoint
        body: Payload da requisição
        max_retries: Número máximo de tentativas
        wait_seconds: Tempo de espera entre retries
        timeout: Timeout da requisição em segundos

    Returns:
        Dict com status_code e response

    Raises:
        EvolutionAPIError: Se todas as tentativas falharem
    """
    headers = {"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"}

    for attempt in range(1, max_retries + 1):
        try:
            log.debug(f"🔄 Tentativa {attempt}/{max_retries}: {url}")
            response = requests.post(url, headers=headers, json=body, timeout=timeout)

            if response.status_code in [200, 201]:
                return {
                    "status_code": response.status_code,
                    "response": response.json(),
                }

            log.warning(
                f"⚠️ Resposta não OK: {response.status_code} - {response.text[:200]}"
            )

        except requests.exceptions.Timeout:
            log.warning(f"⏱ Timeout na tentativa {attempt}")
        except requests.exceptions.RequestException as ex:
            log.warning(f"❌ Erro na tentativa {attempt}: {ex}")

        if attempt < max_retries:
            import time

            time.sleep(wait_seconds)

    raise EvolutionAPIError(
        detail=f"Falha ao comunicar com Evolution API após {max_retries} tentativas"
    )


def processar_imagem(instance: str, message_id: str, ia_infos) -> str:
    """
    Processa imagem enviada e retorna descrição gerada pela IA.

    Args:
        instance: Nome da instância Evolution
        message_id: ID da mensagem contendo a imagem
        ia_infos: Objeto com configurações da IA

    Returns:
        Texto descrevendo a imagem ou mensagem de erro amigável
    """
    log.info(f"🖼️ Processando imagem | instance={instance}, msg_id={message_id}")

    fallback = (
        "Imagem enviada: Desculpe, não consegui processar sua imagem no momento. "
        "Por favor, tente enviar novamente ou descreva o que você gostaria de saber."
    )

    try:
        # 1. Buscar base64 da imagem
        url = f"{EVOLUTION_HOST}chat/getBase64FromMediaMessage/{instance}"
        body = {"message": {"key": {"id": message_id}}, "convertToMp4": False}

        data = _make_request(url, body)
        image_base64 = data["response"]["base64"]

        # 2. Enviar para OpenAI Vision
        api_key = ia_infos.ia_config.credentials.get("api_key") or OPENAI_API_KEY

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": MODEL_ANALYZE_IMAGE,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Descreva detalhadamente o que você vê nesta imagem.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": 500,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        result = response.json()
        transcription = result["choices"][0]["message"]["content"]

        log.info("✅ Imagem transcrita com sucesso")
        return f"Imagem enviada: {transcription}"

    except EvolutionAPIError:
        log.error("❌ Erro ao buscar imagem da Evolution API")
        return fallback
    except requests.exceptions.RequestException as ex:
        log.error(f"❌ Erro na OpenAI Vision API: {ex}")
        return fallback
    except Exception as ex:
        log.exception(f"❌ Erro inesperado ao processar imagem: {ex}")
        return fallback


def processar_audio(instance: str, message_id: str, ia_infos) -> str:
    """
    Processa áudio enviado e retorna transcrição usando Whisper.

    Args:
        instance: Nome da instância Evolution
        message_id: ID da mensagem contendo o áudio
        ia_infos: Objeto com configurações da IA

    Returns:
        Texto transcrito do áudio ou mensagem de erro amigável
    """
    import time

    import openai

    log.info(f"🎧 Processando áudio | instance={instance}, msg_id={message_id}")

    fallback = (
        "Áudio enviado: Desculpe, não consegui processar seu áudio. "
        "Por favor, escreva sua mensagem em texto."
    )

    timestamp = str(time.time())
    audio_path = f"audio_{timestamp}.ogg"
    mp3_path = f"audio_{timestamp}.mp3"

    try:
        # 1. Buscar áudio
        url = f"{EVOLUTION_HOST}chat/getBase64FromMediaMessage/{instance}"
        body = {"message": {"key": {"id": message_id}}, "convertToMp4": False}

        data = _make_request(url, body)
        audio_base64 = data["response"]["base64"]

        # 2. Salvar temporariamente
        audio_bytes = base64.b64decode(audio_base64)
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        # 3. Converter OGG -> MP3
        audio = AudioSegment.from_ogg(audio_path)
        audio.export(mp3_path, format="mp3")

        # 4. Transcrever com Whisper
        api_key = ia_infos.ia_config.credentials.get("api_key") or OPENAI_API_KEY
        openai.api_key = api_key

        with open(mp3_path, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )

        transcription = response.text
        log.info("✅ Áudio transcrito com sucesso")
        return f"Áudio enviado: {transcription}"

    except Exception as ex:
        log.exception(f"❌ Erro ao processar áudio: {ex}")
        return fallback

    finally:
        # Limpar arquivos temporários
        for path in [audio_path, mp3_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass


def send_message(
    instance: str, lead_phone: str, message: str, delay: int = 0
) -> Dict[str, Any]:
    """
    Envia mensagem de texto via Evolution API.

    Args:
        instance: Nome da instância
        lead_phone: Número do destinatário
        message: Texto da mensagem
        delay: Delay em segundos antes de enviar

    Returns:
        Dict com status_code e response

    Raises:
        EvolutionAPIError: Se falhar após retries
    """
    url = f"{EVOLUTION_HOST}message/sendText/{instance}"

    log.info(
        f"📤 Enviando mensagem | lead={lead_phone}, delay={delay}s, "
        f"chars={len(message)}"
    )

    body = {
        "number": lead_phone,
        "text": str(message),
        "delay": int(delay) * 1000,  # converte para ms
        "linkPreview": True,
    }

    return _make_request(url, body, max_retries=5, wait_seconds=3)
