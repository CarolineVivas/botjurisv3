from pydantic import BaseModel


class IAConfig(BaseModel):
    nome: str
    status: bool
    api_key: str
    ia_model: str
    prompt_text: str | None = None
