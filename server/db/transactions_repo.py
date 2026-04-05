"""
PostgreSQL repository for imported transactions and analysis snapshots.
"""

import json
import logging
from typing import Any, Optional

from db.connection import get_conn

logger = logging.getLogger(__name__)


def list_transactions_db(user_id: str, limit: int = 200) -> list[dict]:
    with get_conn() as conn:
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, user_id, date, month, description, counterparty, amount,
                           gross_amount, balance, direction, type, category, status,
                           payment_method, external_id, merchant_order_id, source,
                           source_file, source_format, note, raw, created_at
                    FROM transactions
                    WHERE user_id = %s
                    ORDER BY date ASC, id ASC
                    LIMIT %s
                    """,
                    (user_id, limit),
                )
                rows = cur.fetchall()
            results = []
            for row in rows:
                results.append(
                    {
                        "id": str(row[0]),
                        "user_id": row[1],
                        "date": row[2].isoformat(),
                        "month": row[3],
                        "description": row[4],
                        "counterparty": row[5],
                        "amount": float(row[6]),
                        "gross_amount": float(row[7]),
                        "balance": float(row[8]) if row[8] is not None else None,
                        "direction": row[9],
                        "type": row[10],
                        "category": row[11],
                        "status": row[12],
                        "payment_method": row[13],
                        "external_id": row[14],
                        "merchant_order_id": row[15],
                        "source": row[16],
                        "source_file": row[17],
                        "source_format": row[18],
                        "note": row[19],
                        "raw": row[20],
                        "created_at": row[21].isoformat(),
                    }
                )
            return results
        except Exception:
            logger.exception("Failed to list transactions for user=%s", user_id)
            return []


def replace_transactions_db(user_id: str, transactions: list[dict[str, Any]]) -> bool:
    with get_conn() as conn:
        if not conn:
            return False
        try:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM transactions WHERE user_id = %s", (user_id,))
                    for tx in transactions:
                        cur.execute(
                            """
                            INSERT INTO transactions (
                                user_id, date, month, description, counterparty, amount,
                                gross_amount, balance, direction, type, category, status,
                                payment_method, external_id, merchant_order_id, source,
                                source_file, source_format, note, raw
                            )
                            VALUES (
                                %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s, %s::jsonb
                            )
                            """,
                            (
                                user_id,
                                tx["date"],
                                tx["month"],
                                tx.get("description", ""),
                                tx.get("counterparty", ""),
                                tx.get("amount", 0),
                                tx.get("gross_amount", abs(tx.get("amount", 0))),
                                tx.get("balance"),
                                tx.get("direction", ""),
                                tx.get("type", ""),
                                tx.get("category", "other"),
                                tx.get("status", ""),
                                tx.get("payment_method", ""),
                                tx.get("external_id", ""),
                                tx.get("merchant_order_id", ""),
                                tx.get("source", "manual"),
                                tx.get("source_file", ""),
                                tx.get("source_format", ""),
                                tx.get("note", ""),
                                json.dumps(tx.get("raw", {}), ensure_ascii=False),
                            ),
                        )
            return True
        except Exception:
            logger.exception("Failed to replace transactions for user=%s", user_id)
            return False


def get_latest_analysis_run_db(user_id: str) -> Optional[dict]:
    with get_conn() as conn:
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, user_id, created_at, period_start, period_end,
                           monthly_totals, input, output, source
                    FROM analysis_runs
                    WHERE user_id = %s
                    ORDER BY created_at DESC, id DESC
                    LIMIT 1
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
            if not row:
                return None
            return {
                "id": str(row[0]),
                "user_id": row[1],
                "created_at": row[2].isoformat(),
                "period_start": row[3].isoformat() if row[3] else None,
                "period_end": row[4].isoformat() if row[4] else None,
                "monthly_totals": row[5],
                "input": row[6],
                "output": row[7],
                "source": row[8],
            }
        except Exception:
            logger.exception("Failed to get latest analysis run for user=%s", user_id)
            return None


def replace_latest_analysis_run_db(
    user_id: str,
    period_start: Optional[str],
    period_end: Optional[str],
    monthly_totals: list[dict[str, Any]],
    input_payload: dict[str, Any],
    output_payload: dict[str, Any],
    source: str = "statement_import",
) -> bool:
    with get_conn() as conn:
        if not conn:
            return False
        try:
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM analysis_runs WHERE user_id = %s", (user_id,))
                    cur.execute(
                        """
                        INSERT INTO analysis_runs (
                            user_id, period_start, period_end, monthly_totals, input, output, source
                        )
                        VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s)
                        """,
                        (
                            user_id,
                            period_start,
                            period_end,
                            json.dumps(monthly_totals, ensure_ascii=False),
                            json.dumps(input_payload, ensure_ascii=False),
                            json.dumps(output_payload, ensure_ascii=False),
                            source,
                        ),
                    )
            return True
        except Exception:
            logger.exception("Failed to replace analysis run for user=%s", user_id)
            return False
