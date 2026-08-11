import sqlite3
from contextlib import contextmanager

DB_PATH = "triage.db"


@contextmanager
def get_db():
    """Контекстный менеджер: сам открывает и закрывает соединение с БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # получаем словари вместо кортежей
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Создаёт таблицу tickets, если её ещё нет."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                client_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                text TEXT NOT NULL,
                category TEXT,
                confidence TEXT,
                escalate INTEGER,
                draft_reply TEXT,
                error TEXT
            )
        """)


def save_ticket(
    client_id: str,
    channel: str,
    text: str,
    category: str = None,
    confidence: str = None,
    escalate: bool = None,
    draft_reply: str = None,
    error: str = None,
) -> int:
    """Сохраняет обращение в БД и возвращает его ID."""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tickets
                (client_id, channel, text, category, confidence, escalate, draft_reply, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                client_id,
                channel,
                text,
                category,
                confidence,
                int(escalate) if escalate is not None else None,
                draft_reply,
                error,
            ),
        )
        return cursor.lastrowid


# При импорте сразу создаём таблицу
init_db()