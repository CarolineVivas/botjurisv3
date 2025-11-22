# app/schemas/response.py
from pydantic import BaseModel


class WebhookResponseDTO(BaseModel):
    message: str
    status: str = "ok"


class ErrorDTO(BaseModel):
    message: str
    status: str = "error"
