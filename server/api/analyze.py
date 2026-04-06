"""
/analyze endpoint - Original analysis pipeline.
"""

import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models.analysis import AnalyzeRequest
from services.anomalies import detect_anomalies
from services.categorizer import enrich_transactions
from services.llm import get_llm, llm_json_reply
from services.summaries import build_category_summary

logger = logging.getLogger(__name__)
router = APIRouter()

ANALYZE_SYSTEM_PROMPT = """
You are a professional personal finance analyst.
Return ONLY valid JSON with keys:
insights (array of strings),
actions (array of strings),
budget (object with keys: rules, monthly_targets),
notes (string).
Do not include markdown.
"""


@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        llm = get_llm()
        txns = enrich_transactions(req.transactions)
        anomalies = detect_anomalies(txns)
        category_summary = build_category_summary(txns)
        payload = {
            "user_id": req.user_id,
            "monthly_totals": req.monthly_totals,
            "category_summary": category_summary,
            "anomalies": anomalies,
            "transactions_sample": txns[:30],
        }
        llm_out = llm_json_reply(llm, ANALYZE_SYSTEM_PROMPT, payload)
        return {
            "ok": True,
            "meta": {"user_id": req.user_id, "currency": "CNY"},
            "monthly_totals": req.monthly_totals,
            "category_summary": category_summary,
            "anomalies": anomalies,
            **llm_out,
            "debug": {"rule_version": "v1", "model": "langchain"},
        }
    except Exception:
        logger.exception("Analysis failed for user=%s", req.user_id)
        return JSONResponse(status_code=500, content={"ok": False, "error": "Analysis failed"})
