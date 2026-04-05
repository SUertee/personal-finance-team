"""
Chat-related Pydantic models: request and response.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    user_id: str = "demo"


class ChatResponse(BaseModel):
    reply: str
    agent_used: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
