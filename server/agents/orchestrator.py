"""
Orchestrator Agent - Uses LangGraph StateGraph for multi-agent collaboration
"""

from agents.graph import build_agent_graph
from services.memory import get_chat_history, save_message
from services.user_store import get_profile

_graph = build_agent_graph()


async def handle_message(user_id: str, message: str, transactions: list[dict] | None = None, monthly_totals: list[dict] | None = None) -> dict:
    profile = get_profile(user_id)
    chat_history = get_chat_history(user_id)
    state = {"user_id": user_id, "message": message, "profile": profile.model_dump(), "transactions": transactions or [], "monthly_totals": monthly_totals or [], "chat_history": chat_history, "routed_agent": "", "refined_query": "", "agent_reply": "", "agent_data": None, "needs_advisor_review": False, "advisor_comment": "", "final_reply": "", "agent_used": ""}
    result = await _graph.ainvoke(state)
    save_message(user_id, "user", message)
    save_message(user_id, "assistant", result["final_reply"])
    return {"reply": result["final_reply"], "agent_used": result.get("agent_used", "general"), "data": result.get("agent_data")}
