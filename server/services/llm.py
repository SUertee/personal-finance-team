"""
llm.py
- Supports both Ollama (local) and OpenAI (cloud).
- Set LLM_PROVIDER=openai to use OpenAI, defaults to Ollama.
"""

import json
import os

from langchain_core.messages import HumanMessage, SystemMessage


def get_llm():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o"), api_key=os.getenv("OPENAI_API_KEY", ""), temperature=0.2)
    from langchain_ollama import ChatOllama
    model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    base_url = os.getenv("OLLAMA_BASE_URL")
    if base_url:
        return ChatOllama(model=model, temperature=0.2, base_url=base_url)
    return ChatOllama(model=model, temperature=0.2)


def llm_json_reply(llm, system_prompt: str, payload: dict) -> dict:
    res = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=json.dumps(payload, default=str))])
    content = res.content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        return json.loads(content)
    except Exception:
        return {"insights": [], "actions": [], "budget": {}, "notes": content}
