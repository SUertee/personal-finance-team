"""
News Scout Agent - Fetches real news via NewsAPI, analyzes for user
"""
from langchain_core.messages import HumanMessage, SystemMessage
from agents.context_utils import build_profile_summary
from models.user import UserProfile
from services.llm import get_llm
from services.news_api import fetch_news

SYSTEM_PROMPT = """You are a financial news analyst. You receive REAL news articles.
1. Summarize key news relevant to user
2. Identify opportunities and risks
3. Rate impact (1-5)
4. Provide actionable insights
Cite sources. Respond in user's language."""

def _fmt_news(articles):
    if not articles: return "No news found."
    return "\n\n".join(f"[{i}] {a.get('title','')}\n    Source: {a.get('source','')} | {a.get('published_at','')}\n    {a.get('description','')}" for i, a in enumerate(articles, 1))

async def scout_news(profile: UserProfile, query: str) -> str:
    articles = await fetch_news(query, page_size=8)
    llm = get_llm()
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=f"Profile:\n{build_profile_summary(profile)}\n\n=== News ===\n{_fmt_news(articles)}\n\nQuery: {query}")])
    return response.content
