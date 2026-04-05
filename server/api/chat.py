"""
/chat endpoints - Multi-agent chat and history management.
"""

from fastapi import APIRouter

from agents.orchestrator import handle_message
from models.chat import ChatRequest, ChatResponse
from services.memory import clear_history, get_chat_history

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    result = await handle_message(user_id=req.user_id, message=req.message)
    return ChatResponse(**result)


@router.get("/chat/history/{user_id}")
def get_history(user_id: str, limit: int = 50):
    return {"user_id": user_id, "messages": get_chat_history(user_id, limit)}


@router.delete("/chat/history/{user_id}")
def delete_history(user_id: str):
    clear_history(user_id)
    return {"ok": True, "message": f"Chat history cleared for {user_id}"}
