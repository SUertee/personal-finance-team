"""
Advisor Agent - Financial advice, asset allocation, investment suggestions
"""
from langchain_core.messages import HumanMessage, SystemMessage
from agents.context_utils import build_agent_context
from models.user import UserProfile
from services.llm import get_llm

SYSTEM_PROMPT = """You are a personal financial advisor. Provide:
1. Asset Allocation 2. Savings Strategy 3. Debt Management 4. Investment Suggestions 5. Risk Assessment
Note: AI-generated advice. Be specific with numbers. Respond in user's language."""

async def advise(profile: UserProfile, transactions: list[dict], monthly_totals: list[dict], query: str) -> str:
    llm = get_llm()
    ctx = build_agent_context(profile, transactions, monthly_totals, monthly_limit=6)
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Profile:\n{ctx}\n\nQuestion: {query}")])
    return response.content
