"""
Insight Agent - Strategic trend analysis, future projections
"""
from collections import defaultdict
from langchain_core.messages import HumanMessage, SystemMessage
from models import UserProfile
from services.llm import get_llm

SYSTEM_PROMPT = """You are a strategic financial insight analyst. Provide:
1. Trend Analysis 2. Future Projections (3/6/12 months) 3. Opportunity Windows 4. Risk Radar 5. Life Stage Assessment 6. Strategic Recommendations
Respond in user's language."""

def _ctx(profile, transactions, monthly_totals):
    lines = [f"Name: {profile.name or 'Unknown'}", f"Occupation: {profile.occupation or 'Unknown'}", f"Risk: {profile.risk_tolerance}", f"Goals: {', '.join(profile.financial_goals) or 'Not set'}", f"Cash: {profile.assets.cash_balance:,.2f} | Savings: {profile.assets.savings:,.2f}", f"Investments: {profile.assets.investments:,.2f} | Liabilities: {profile.assets.liabilities:,.2f}", f"Net Worth: {profile.assets.net_worth:,.2f}", f"Income: {profile.monthly_income:,.2f} | Expenses: {profile.monthly_expenses:,.2f}"]
    if monthly_totals:
        for m in monthly_totals: lines.append(f"  {m.get('month','?')}: inc={m.get('income',0):,.2f} exp={m.get('expense',0):,.2f} net={m.get('net',0):,.2f}")
    if transactions:
        ms, ct = defaultdict(float), defaultdict(float)
        for t in transactions:
            amt = t.get('amount', 0)
            if isinstance(amt, (int,float)) and amt < 0:
                ms[t.get('date','')[:7]] += abs(amt)
                ct[t.get('category','other')] += abs(amt)
        for m in sorted(ms): lines.append(f"  {m}: {ms[m]:,.2f}")
        for c, v in sorted(ct.items(), key=lambda x: -x[1]): lines.append(f"  {c}: {v:,.2f}")
    if profile.notes: lines.append(f"Notes: {profile.notes}")
    return "\n".join(lines)

async def generate_insights(profile: UserProfile, transactions: list[dict], monthly_totals: list[dict], query: str) -> str:
    llm = get_llm()
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Data:\n{_ctx(profile, transactions, monthly_totals)}\n\nRequest: {query}")])
    return response.content
