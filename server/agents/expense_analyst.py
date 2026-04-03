"""
Expense Analyst Agent - Deterministic services + LLM narrative
"""
from services.anomalies import detect_anomalies
from services.categorizer import enrich_transactions
from services.llm import get_llm, llm_json_reply
from services.summaries import build_category_summary

SYSTEM_PROMPT = """You are an expense analyst. Return ONLY valid JSON:
{"summary": "Brief expense summary", "top_categories": ["insights"], "anomalies_commentary": "commentary", "recommendations": ["recommendations"]}
Respond in same language as user query. Be specific with numbers."""

async def analyze_expenses(transactions: list[dict], monthly_totals: list[dict], query: str) -> dict:
    llm = get_llm()
    enriched = enrich_transactions(transactions)
    anomalies = detect_anomalies(enriched)
    category_summary = build_category_summary(enriched)
    payload = {"user_query": query, "monthly_totals": monthly_totals, "category_summary": category_summary, "anomalies": anomalies, "transaction_count": len(enriched), "sample_transactions": enriched[:20]}
    llm_out = llm_json_reply(llm, SYSTEM_PROMPT, payload)
    return {"analysis": llm_out, "category_summary": category_summary, "anomalies": anomalies}
