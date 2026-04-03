"""
app.py
- FastAPI entrypoint for the Finance AI Multi-Agent System.
- Endpoints:
  - GET  /schema           - JSON schema for frontend
  - POST /analyze          - Original analysis pipeline (unchanged)
  - POST /chat             - Multi-agent chat (new)
  - GET  /profile/{id}     - Get user profile (new)
  - PUT  /profile/{id}     - Update user profile (new)
  - GET  /health           - Health check (new)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.orchestrator import handle_message
from memory import clear_history, get_chat_history
from models import (
    AnalyzeRequest,
    ChatRequest,
    ChatResponse,
    ProfileUpdateRequest,
)
from services.anomalies import detect_anomalies
from services.categorizer import enrich_transactions
from services.llm import get_llm, llm_json_reply
from services.schema import FINANCE_ANALYSIS_SCHEMA
from services.summaries import build_category_summary
from user_store import get_profile, update_profile

app = FastAPI(
    title="Finance AI Multi-Agent System",
    description=(
        "Personal finance analysis system with LangChain multi-agent architecture. "
        "Features: expense analysis, budget analysis, news scouting, financial advising, and strategic insights."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ANALYZE_SYSTEM_PROMPT = """
You are a professional personal finance analyst.
Return ONLY valid JSON with keys:
insights (array of strings),
actions (array of strings),
budget (object with keys: rules, monthly_targets),
notes (string).
Do not include markdown.
"""


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "agents": [
        "expense_analyst", "budget_analyst", "news_scout", "advisor", "insight"
    ]}


@app.get("/schema")
def schema():
    return FINANCE_ANALYSIS_SCHEMA


@app.post("/analyze")
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
            "meta": {"user_id": req.user_id, "currency": "AUD"},
            "monthly_totals": req.monthly_totals,
            "category_summary": category_summary,
            "anomalies": anomalies,
            **llm_out,
            "debug": {"rule_version": "v1", "model": "langchain"},
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = await handle_message(user_id=req.user_id, message=req.message)
    return ChatResponse(**result)


@app.get("/profile/{user_id}")
def get_user_profile(user_id: str):
    p = get_profile(user_id)
    return p.model_dump()


@app.put("/profile/{user_id}")
def update_user_profile(user_id: str, req: ProfileUpdateRequest):
    p = update_profile(user_id, req)
    return p.model_dump()


@app.get("/chat/history/{user_id}")
def get_history(user_id: str, limit: int = 50):
    return {"user_id": user_id, "messages": get_chat_history(user_id, limit)}


@app.delete("/chat/history/{user_id}")
def delete_history(user_id: str):
    clear_history(user_id)
    return {"ok": True, "message": f"Chat history cleared for {user_id}"}
