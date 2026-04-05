"""
Insight Agent - Strategic trend analysis, future projections
"""
from langchain_core.messages import HumanMessage, SystemMessage
from agents.context_utils import build_agent_context
from models.user import UserProfile
from services.llm import get_llm

SYSTEM_PROMPT = """You are a strategic financial insight analyst. Provide:
1. Trend Analysis 2. Future Projections (3/6/12 months) 3. Opportunity Windows 4. Risk Radar 5. Life Stage Assessment 6. Strategic Recommendations
Respond in user's language."""

async def generate_insights(profile: UserProfile, transactions: list[dict], monthly_totals: list[dict], query: str) -> str:
    llm = get_llm()
    ctx = build_agent_context(profile, transactions, monthly_totals, include_monthly_net=True)
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Data:\n{ctx}\n\nRequest: {query}")])
    return response.content
