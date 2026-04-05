"""
/transactions and /analysis-runs endpoints for frontend dashboards.
"""

from fastapi import APIRouter

from db.transactions_repo import get_latest_analysis_run_db, list_transactions_db

router = APIRouter()


@router.get("/transactions/{user_id}")
def get_transactions(user_id: str, limit: int = 500):
    return {"user_id": user_id, "items": list_transactions_db(user_id, limit)}


@router.get("/analysis-runs/latest/{user_id}")
def get_latest_analysis_run(user_id: str):
    return get_latest_analysis_run_db(user_id)
