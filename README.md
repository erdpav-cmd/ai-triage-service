# 🤖 AI Triage Service — ИИ-сервис первичной обработки обращений

**Проблема:** менеджеры тратят время на ручную сортировку обращений → падает скорость реакции.
**Решение:** API + LLM классифицирует обращение, пишет черновик ответа, передаёт сложные случаи человеку.
**Результат:** быстрее реакция, ниже нагрузка, прозрачная история обращений.

## 🛠 Стек

- Python 3.10+, FastAPI
- LLM (через ProxyApi, OpenAI-совместимый API)
- SQLite (аудит)
- Docker

## 🚀 Локальный запуск (5–10 минут)

1. Клонируй репозиторий:
```bash
git clone <ссылка_на_репозиторий>
cd ai-triage-service
```

2. Создай виртуальное окружение и установи зависимости:
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

3. Создай `.env` по образцу `.env.example` и впиши свой ключ LLM.

4. Запусти сервис:
```bash
uvicorn app.main:app --reload
```

5. Открой http://127.0.0.1:8000/docs и отправь запрос.

## 📮 Пример запроса

```bash
curl -X POST http://127.0.0.1:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Мне дважды списали деньги за заказ №1234!",
    "channel": "email",
    "client_id": "client-001"
  }'
```

**Пример ответа:**
```json
{
  "category": "billing",
  "draft_reply": "Здравствуйте! Спасибо за обращение...",
  "confidence": "high",
  "escalate": false,
  "ticket_id": 1
}
```

## 🐳 Запуск в Docker

```bash
docker build -t ai-triage-service .
docker run --env-file .env -p 8000:8000 ai-triage-service
```

## 💾 Где смотреть данные

- **SQLite:** файл `triage.db` в корне проекта (таблица `tickets` — журнал обращений, включая ошибки)
- **Логи:** вывод терминала, где запущен uvicorn

## 🛡 Надёжность и безопасность

- Валидация входа (длина текста 1–2000, обязательные поля)
- Секреты только через `.env` (не в коде и не в образе Docker)
- Лимит: не более N запросов/мин на `client_id` (настройка в `.env`)
- Сценарий «если всё сломалось»: при ошибке LLM → `escalate=true` + шаблон «передано оператору», ошибка пишется в БД

## 👤 Автор

Павел Эрдниев | Junior Python Developer
📬 Telegram: @Erdpav
🔗 GitHub: https://github.com/erdpav-cmd