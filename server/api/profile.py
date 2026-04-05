"""
/profile endpoints - User profile management.
"""

from fastapi import APIRouter

from models.user import ProfileUpdateRequest
from services.user_store import get_profile, update_profile

router = APIRouter()


@router.get("/profile/{user_id}")
def get_user_profile(user_id: str):
    p = get_profile(user_id)
    return p.model_dump()


@router.put("/profile/{user_id}")
def update_user_profile(user_id: str, req: ProfileUpdateRequest):
    p = update_profile(user_id, req)
    return p.model_dump()
