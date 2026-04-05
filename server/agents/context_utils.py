"""
Shared context-building utilities for agents.
"""

from collections import defaultdict

from models.user import UserProfile


def build_profile_lines(profile: UserProfile) -> list[str]:
    """Common profile header lines used by multiple agents."""
    return [
        f"Name: {profile.name or 'Unknown'}",
        f"Occupation: {profile.occupation or 'Unknown'}",
        f"Risk: {profile.risk_tolerance}",
        f"Goals: {', '.join(profile.financial_goals) or 'Not set'}",
        f"Cash: {profile.assets.cash_balance:,.2f}",
        f"Savings: {profile.assets.savings:,.2f}",
        f"Investments: {profile.assets.investments:,.2f}",
        f"Liabilities: {profile.assets.liabilities:,.2f}",
        f"Net Worth: {profile.assets.net_worth:,.2f}",
        f"Income: {profile.monthly_income:,.2f}",
        f"Expenses: {profile.monthly_expenses:,.2f}",
    ]


def build_monthly_totals_lines(monthly_totals: list[dict], *, limit: int | None = None, include_net: bool = False) -> list[str]:
    """Format monthly totals into display lines."""
    data = monthly_totals[-limit:] if limit else monthly_totals
    lines = []
    for m in data:
        base = f"  {m.get('month', '?')}: inc={m.get('income', 0):,.2f} exp={m.get('expense', 0):,.2f}"
        if include_net:
            base += f" net={m.get('net', 0):,.2f}"
        lines.append(base)
    return lines


def build_spending_by_category(transactions: list[dict]) -> list[str]:
    """Aggregate spending by category from transactions."""
    ct: dict[str, float] = defaultdict(float)
    for t in transactions:
        amt = t.get("amount", 0)
        if isinstance(amt, (int, float)) and amt < 0:
            ct[t.get("category", "other")] += abs(amt)
    return [f"  {c}: {v:,.2f}" for c, v in sorted(ct.items(), key=lambda x: -x[1])]


def build_agent_context(
    profile: UserProfile,
    transactions: list[dict],
    monthly_totals: list[dict],
    *,
    monthly_limit: int | None = None,
    include_monthly_net: bool = False,
) -> str:
    """Full context string for agents that need profile + financial data."""
    lines = build_profile_lines(profile)
    if monthly_totals:
        lines.extend(build_monthly_totals_lines(monthly_totals, limit=monthly_limit, include_net=include_monthly_net))
    if transactions:
        lines.extend(build_spending_by_category(transactions))
    if profile.notes:
        lines.append(f"Notes: {profile.notes}")
    return "\n".join(lines)


def build_profile_summary(profile: UserProfile) -> str:
    """Minimal profile context for agents that only need user info (e.g. news_scout)."""
    lines = [
        f"Name: {profile.name or 'Unknown'}",
        f"Occupation: {profile.occupation or 'Unknown'}",
        f"Risk: {profile.risk_tolerance}",
        f"Goals: {', '.join(profile.financial_goals) or 'Not set'}",
        f"Net Worth: {profile.assets.net_worth:,.2f}",
    ]
    if profile.notes:
        lines.append(f"Notes: {profile.notes}")
    return "\n".join(lines)
