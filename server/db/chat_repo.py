"""
PostgreSQL repository for chat history.
"""

from datetime import datetime, timezone

from db.connection import get_conn


def get_chat_history_db(user_id: str, limit: int = 50) -> list[dict]:
    conn = get_conn()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT role, content
                FROM chat_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            rows = cur.fetchall()
        rows.reverse()
        return [{"role": row[0], "content": row[1]} for row in rows]
    except Exception:
        return []


def save_message_db(user_id: str, role: str, content: str) -> bool:
    conn = get_conn()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat_history (user_id, role, content, created_at)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, role, content, datetime.now(timezone.utc)),
            )
        return True
    except Exception:
        return False


def clear_history_db(user_id: str) -> bool:
    conn = get_conn()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM chat_history WHERE user_id = %s", (user_id,))
        return True
    except Exception:
        return False
