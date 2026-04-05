"""
Orchestrator Agent - Uses LangGraph StateGraph for multi-agent collaboration
"""

import logging

from agents.graph import build_agent_graph
from services.memory import get_chat_history, save_message
from services.user_store import get_profile

logger = logging.getLogger(__name__)

_graph = build_agent_graph()


async def handle_message(user_id: str, message: str, transactions: list[dict] | None = None, monthly_totals: list[dict] | None = None) -> dict:
    profile = get_profile(user_id)
    chat_history = get_chat_history(user_id)
    state = {"user_id": user_id, "message": message, "profile": profile.model_dump(), "transactions": transactions or [], "monthly_totals": monthly_totals or [], "chat_history": chat_history, "routed_agent": "", "refined_query": "", "agent_reply": "", "agent_data": None, "needs_advisor_review": False, "advisor_comment": "", "final_reply": "", "agent_used": ""}
    try:
        result = await _graph.ainvoke(state)
    except Exception:
        logger.exception("Graph invocation failed for user=%s", user_id)
        return {"reply": "Sorry, something went wrong. Please try again.", "agent_used": "error", "data": None}
    save_message(user_id, "user", message)
    save_message(user_id, "assistant", result["final_reply"])
    logger.info("Handled message for user=%s, agent=%s", user_id, result.get("agent_used", "general"))
    return {"reply": result["final_reply"], "agent_used": result.get("agent_used", "general"), "data": result.get("agent_data")}
