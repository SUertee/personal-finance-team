"""
Health check and schema endpoints.
"""

from fastapi import APIRouter

from services.schema import FINANCE_ANALYSIS_SCHEMA

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "agents": [
            "expense_analyst",
            "budget_analyst",
            "news_scout",
            "advisor",
            "insight",
        ],
    }


@router.get("/schema")
def schema():
    return FINANCE_ANALYSIS_SCHEMA
