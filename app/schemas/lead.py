from typing import List, Optional

from pydantic import BaseModel


class LeadMessage(BaseModel):
    role: str
    name: Optional[str]
    content: str


class LeadSchema(BaseModel):
    id: Optional[int]
    phone: str
    name: str
    messages: List[LeadMessage]
    resume: Optional[str]
