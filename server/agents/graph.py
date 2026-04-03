"""
graph.py - LangGraph StateGraph for multi-agent collaboration.
Flow: Router -> Specialist Agent -> (optional) Advisor Review -> Response
"""

from __future__ import annotations
import json
from typing import Literal
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from agents import advisor, budget_analyst, expense_analyst, insight, news_scout
from models import UserProfile
from services.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage


class AgentState(TypedDict):
    user_id: str
    message: str
    profile: dict
    transactions: list[dict]
    monthly_totals: list[dict]
    chat_history: list[dict]
    routed_agent: str
    refined_query: str
    agent_reply: str
    agent_data: dict | None
    needs_advisor_review: bool
    advisor_comment: str
    final_reply: str
    agent_used: str


ROUTER_PROMPT = """You are the orchestrator of a personal finance AI system. Route to the correct agent.
Available: "expense_analyst", "budget_analyst", "news_scout", "advisor", "insight", "general".
Set "needs_review" true for complex queries.
Respond with ONLY JSON: {"agent": "<name>", "refined_query": "<query>", "needs_review": false}"""


def router_node(state: AgentState) -> dict:
    llm = get_llm()
    profile = state["profile"]
    context = f"User: {profile.get('name', 'Unknown')}, Goals: {', '.join(profile.get('financial_goals', []))}"
    history_text = ""
    if state.get("chat_history"):
        recent = state["chat_history"][-6:]
        history_text = "\nRecent: " + "; ".join(f"{m['role']}: {m['content'][:100]}" for m in recent)
    response = llm.invoke([SystemMessage(content=ROUTER_PROMPT), HumanMessage(content=f"Context: {context}{history_text}\nMessage: {state['message']}")])
    content = response.content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        routing = json.loads(content)
    except Exception:
        routing = {"agent": "general", "refined_query": state["message"], "needs_review": False}
    return {"routed_agent": routing.get("agent", "general"), "refined_query": routing.get("refined_query", state["message"]), "needs_advisor_review": routing.get("needs_review", False)}


async def agent_dispatch_node(state: AgentState) -> dict:
    agent_name = state["routed_agent"]
    query = state["refined_query"]
    profile = UserProfile(**state["profile"])
    txns = state.get("transactions", [])
    totals = state.get("monthly_totals", [])
    if agent_name == "expense_analyst":
        result = await expense_analyst.analyze_expenses(txns, totals, query)
        analysis = result.get("analysis", {})
        parts = []
        if analysis.get("summary"): parts.append(analysis["summary"])
        if analysis.get("top_categories"): parts.append("\n".join(f"- {c}" for c in analysis["top_categories"]))
        if analysis.get("anomalies_commentary"): parts.append(analysis["anomalies_commentary"])
        if analysis.get("recommendations"): parts.append("Recommendations:\n" + "\n".join(f"- {r}" for r in analysis["recommendations"]))
        return {"agent_reply": "\n\n".join(parts) if parts else str(analysis), "agent_data": {"category_summary": result.get("category_summary"), "anomalies": result.get("anomalies")}, "agent_used": agent_name}
    if agent_name == "budget_analyst":
        reply = await budget_analyst.analyze_budget(profile, txns, totals, query)
        return {"agent_reply": reply, "agent_data": None, "agent_used": agent_name}
    if agent_name == "news_scout":
        reply = await news_scout.scout_news(profile, query)
        return {"agent_reply": reply, "agent_data": None, "agent_used": agent_name}
    if agent_name == "advisor":
        reply = await advisor.advise(profile, txns, totals, query)
        return {"agent_reply": reply, "agent_data": None, "agent_used": agent_name}
    if agent_name == "insight":
        reply = await insight.generate_insights(profile, txns, totals, query)
        return {"agent_reply": reply, "agent_data": None, "agent_used": agent_name}
    # general
    llm = get_llm()
    prompt = f"You are a friendly finance AI. User: {state['profile'].get('name', 'Unknown')}. Respond in user's language."
    messages = [SystemMessage(content=prompt)]
    if state.get("chat_history"):
        for m in state["chat_history"][-10:]:
            if m["role"] == "user": messages.append(HumanMessage(content=m["content"]))
            else:
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=m["content"]))
    messages.append(HumanMessage(content=state["message"]))
    response = llm.invoke(messages)
    return {"agent_reply": response.content, "agent_data": None, "agent_used": "general"}


async def advisor_review_node(state: AgentState) -> dict:
    profile = UserProfile(**state["profile"])
    llm = get_llm()
    response = llm.invoke([SystemMessage(content="Review this analysis briefly (2-3 sentences). Add actionable advice."), HumanMessage(content=f"User: {profile.name}, Risk: {profile.risk_tolerance}\n\n{state['agent_reply'][:1500]}")])
    return {"advisor_comment": response.content}


def compose_response_node(state: AgentState) -> dict:
    reply = state["agent_reply"]
    if state.get("advisor_comment"):
        reply += f"\n\n---\n**Advisor Note:** {state['advisor_comment']}"
    return {"final_reply": reply}


def should_review(state: AgentState) -> Literal["advisor_review", "compose"]:
    if state.get("needs_advisor_review") and state.get("routed_agent") not in ("advisor", "general"):
        return "advisor_review"
    return "compose"


def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("router", router_node)
    graph.add_node("dispatch", agent_dispatch_node)
    graph.add_node("advisor_review", advisor_review_node)
    graph.add_node("compose", compose_response_node)
    graph.set_entry_point("router")
    graph.add_edge("router", "dispatch")
    graph.add_conditional_edges("dispatch", should_review, {"advisor_review": "advisor_review", "compose": "compose"})
    graph.add_edge("advisor_review", "compose")
    graph.add_edge("compose", END)
    return graph.compile()
