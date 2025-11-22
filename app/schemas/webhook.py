# app/schemas/webhook.py
from typing import Any, Dict, Optional

from pydantic import constr

from .common import PHONE_REGEX, ApiBaseModel, MessageType, Timestamped


class WebhookMessage(ApiBaseModel):
    conversation: Optional[str] = None
    extendedTextMessage: Optional[Dict[str, Any]] = None
    documentWithCaptionMessage: Optional[Dict[str, Any]] = None
    imageMessage: Optional[Dict[str, Any]] = None
    audioMessage: Optional[Dict[str, Any]] = None


class WebhookKey(ApiBaseModel):
    id: constr(min_length=5)  # id precisa ter pelo menos 5 chars
    remoteJid: constr(pattern=PHONE_REGEX)
    fromMe: Optional[bool] = None


class WebhookData(ApiBaseModel):
    key: WebhookKey
    message: WebhookMessage
    messageType: MessageType
    pushName: Optional[constr(min_length=1, max_length=120)] = "Usuário"
    messageTimestamp: Optional[int] = None  # epoch


class WebhookPayload(Timestamped):
    """Envelope do Evolution"""

    apikey: Optional[str] = None
    instance: constr(min_length=1)
    sender: constr(pattern=r"^\d{10,15}@s\.whatsapp\.net$")
    event: Optional[str] = None
    data: WebhookData
