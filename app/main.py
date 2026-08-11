import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from app import database
from app.llm_client import triage_with_llm
from app.models import TriageRequest, TriageResponse
from app.rate_limiter import RateLimiter

load_dotenv()

app = FastAPI(
    title="AI Triage Service",
    description="ИИ-сервис первичной обработки обращений",
    version="1.0.0",
)

rate_limiter = RateLimiter(
    max_requests=int(os.getenv("RATE_LIMIT_PER_MINUTE", 5))
)

FALLBACK_REPLY = "Ваше обращение передано оператору. Мы свяжемся с вами в ближайшее время."


@app.get("/")
def root():
    """Проверка, что сервис жив."""
    return {"status": "ok", "service": "AI Triage Service"}


@app.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest):
    # 1. Проверка лимита
    if not rate_limiter.allow(request.client_id):
        raise HTTPException(
            status_code=429,
            detail="Слишком много запросов. Повторите через минуту.",
        )

    # 2. Обращение к LLM (с защитой от сбоев)
    error_message = None
    try:
        result = triage_with_llm(request.text, request.channel)
        category = result.category
        draft_reply = result.draft_reply
        confidence = result.confidence
        escalate = result.escalate
    except Exception as e:
        # Сценарий «если всё сломалось» → эскалация человеку
        error_message = str(e)
        category = "other"
        draft_reply = FALLBACK_REPLY
        confidence = "low"
        escalate = True

    # 3. Сохраняем в БД (аудит)
    ticket_id = database.save_ticket(
        client_id=request.client_id,
        channel=request.channel,
        text=request.text,
        category=category,
        confidence=confidence,
        escalate=escalate,
        draft_reply=draft_reply,
        error=error_message,
    )

    return TriageResponse(
        category=category,
        draft_reply=draft_reply,
        confidence=confidence,
        escalate=escalate,
        ticket_id=ticket_id,
    )