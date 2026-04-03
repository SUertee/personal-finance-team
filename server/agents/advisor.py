"""
Advisor Agent - Financial advice, asset allocation, investment suggestions
"""
from collections import defaultdict
from langchain_core.messages import HumanMessage, SystemMessage
from models import UserProfile
from services.llm import get_llm

SYSTEM_PROMPT = """You are a personal financial advisor. Provide:
1. Asset Allocation 2. Savings Strategy 3. Debt Management 4. Investment Suggestions 5. Risk Assessment
Note: AI-generated advice. Be specific with numbers. Respond in user's language."""

def _ctx(profile, transactions, monthly_totals):
    lines = [f"Name: {profile.name or 'Unknown'}", f"Occupation: {profile.occupation or 'Unknown'}", f"Risk: {profile.risk_tolerance}", f"Goals: {', '.join(profile.financial_goals) or 'Not set'}", "", f"Cash: {profile.assets.cash_balance:,.2f}", f"Savings: {profile.assets.savings:,.2f}", f"Investments: {profile.assets.investments:,.2f}", f"Liabilities: {profile.assets.liabilities:,.2f}", f"Net Worth: {profile.assets.net_worth:,.2f}", f"Income: {profile.monthly_income:,.2f}", f"Expenses: {profile.monthly_expenses:,.2f}"]
    if monthly_totals:
        for m in monthly_totals[-6:]: lines.append(f"  {m.get('month','?')}: inc={m.get('income',0):,.2f} exp={m.get('expense',0):,.2f}")
    if transactions:
        ct = defaultdict(float)
        for t in transactions:
            if isinstance(t.get('amount'), (int,float)) and t['amount'] < 0: ct[t.get('category','other')] += abs(t['amount'])
        for c, v in sorted(ct.items(), key=lambda x: -x[1]): lines.append(f"  {c}: {v:,.2f}")
    if profile.notes: lines.append(f"Notes: {profile.notes}")
    return "\n".join(lines)

async def advise(profile: UserProfile, transactions: list[dict], monthly_totals: list[dict], query: str) -> str:
    llm = get_llm()
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Profile:\n{_ctx(profile, transactions, monthly_totals)}\n\nQuestion: {query}")])
    return response.content
