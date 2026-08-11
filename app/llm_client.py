import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.models import LLMResponse

load_dotenv()  # загружаем секреты из .env

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),  # ProxyApi вместо OpenAI
)

MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """Ты — ассистент службы поддержки. Твоя задача: классифицировать обращение и написать черновик ответа.

Правила:
1. Отвечай строго по входному тексту, не выдумывай факты.
2. Если данных мало или что-то непонятно — ставь confidence=low и escalate=true.
3. Категории: billing (оплата/возвраты), support (технические вопросы), complaint (жалобы), other (прочее).
4. draft_reply — вежливый черновик ответа клиенту, 1–6 предложений.
5. Верни СТРОГО JSON без лишнего текста:
{"category": "...", "draft_reply": "...", "confidence": "...", "escalate": true}"""


def _extract_json(raw: str) -> dict:
    """Достаёт JSON из ответа модели, даже если вокруг лишний текст."""
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("В ответе модели нет JSON")
    return json.loads(raw[start:end + 1])


def triage_with_llm(text: str, channel: str) -> LLMResponse:
    """Отправляет обращение в LLM и возвращает проверенный ответ."""
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,  # низкая температура = меньше «фантазий»
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Канал: {channel}\nОбращение: {text}"},
        ],
    )
    raw = response.choices[0].message.content
    data = _extract_json(raw)
    return LLMResponse(**data)  # Pydantic проверит поля