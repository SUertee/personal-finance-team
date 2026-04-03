"""
Budget Analyst Agent - Income vs expenses, savings rate, financial health
"""
from models import UserProfile
from services.llm import get_llm, llm_json_reply

SYSTEM_PROMPT = """You are a budget analyst. Return ONLY valid JSON:
{"monthly_summary": "analysis", "savings_rate": "assessment", "health_score": 75, "health_explanation": "why", "spending_patterns": ["patterns"], "recommendations": ["actions"]}
Be data-driven. Respond in same language as user query."""

def _build_context(profile, transactions, monthly_totals):
    return {"user": {"name": profile.name or "Unknown", "occupation": profile.occupation or "Unknown", "risk_tolerance": profile.risk_tolerance, "goals": profile.financial_goals, "monthly_income": profile.monthly_income, "monthly_expenses": profile.monthly_expenses}, "assets": {"cash": profile.assets.cash_balance, "savings": profile.assets.savings, "investments": profile.assets.investments, "liabilities": profile.assets.liabilities, "net_worth": profile.assets.net_worth}, "monthly_totals": monthly_totals, "recent_transactions": transactions[:30], "notes": profile.notes}

async def analyze_budget(profile: UserProfile, transactions: list[dict], monthly_totals: list[dict], query: str) -> str:
    llm = get_llm()
    context = _build_context(profile, transactions, monthly_totals)
    context["user_query"] = query
    result = llm_json_reply(llm, SYSTEM_PROMPT, context)
    parts = []
    if isinstance(result.get("monthly_summary"), str): parts.append(f"Monthly Summary\n{result['monthly_summary']}")
    if isinstance(result.get("savings_rate"), str): parts.append(f"Savings Rate\n{result['savings_rate']}")
    parts.append(f"Financial Health Score: {result.get('health_score', 'N/A')}/100\n{result.get('health_explanation', '')}")
    if result.get("spending_patterns"): parts.append("Spending Patterns\n" + "\n".join(f"  - {p}" for p in result["spending_patterns"]))
    if result.get("recommendations"): parts.append("Recommendations\n" + "\n".join(f"  - {r}" for r in result["recommendations"]))
    return "\n\n".join(parts)
