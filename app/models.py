from typing import Literal

from pydantic import BaseModel, Field


# Входящий запрос
class TriageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Текст обращения")
    channel: Literal["email", "form", "chat"] = Field(..., description="Источник обращения")
    client_id: str = Field(..., description="ID клиента")


# Ответ от LLM (промежуточный)
class LLMResponse(BaseModel):
    category: Literal["billing", "support", "complaint", "other"]
    draft_reply: str
    confidence: Literal["high", "medium", "low"]
    escalate: bool


# Финальный ответ API
class TriageResponse(BaseModel):
    category: Literal["billing", "support", "complaint", "other"]
    draft_reply: str
    confidence: Literal["high", "medium", "low"]
    escalate: bool
    ticket_id: int = Field(..., description="ID записи в БД")