"""
mongo_store.py - MongoDB persistence for profiles and chat history.
"""

import os
from datetime import datetime, timezone
from typing import Optional
from models import AssetSnapshot, UserProfile

_client = None
_db = None


def _get_db():
    global _client, _db
    if _db is not None:
        return _db
    mongo_uri = os.getenv("MONGODB_URI", "")
    db_name = os.getenv("MONGODB_DB", "finance_ai")
    if not mongo_uri:
        return None
    try:
        from pymongo import MongoClient
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        _client.admin.command("ping")
        _db = _client[db_name]
        _db["chat_history"].create_index([("user_id", 1), ("created_at", -1)])
        return _db
    except Exception:
        return None


def get_profile_db(user_id: str) -> Optional[UserProfile]:
    db = _get_db()
    if not db:
        return None
    try:
        doc = db["user_profiles"].find_one({"user_id": user_id})
        if not doc:
            return None
        return UserProfile(user_id=doc["user_id"], name=doc.get("name", ""), occupation=doc.get("occupation", ""), financial_goals=doc.get("financial_goals", []), risk_tolerance=doc.get("risk_tolerance", "moderate"), assets=AssetSnapshot(cash_balance=float(doc.get("cash_balance", 0)), savings=float(doc.get("savings", 0)), investments=float(doc.get("investments", 0)), liabilities=float(doc.get("liabilities", 0))), monthly_income=float(doc.get("monthly_income", 0)), monthly_expenses=float(doc.get("monthly_expenses", 0)), notes=doc.get("notes", ""))
    except Exception:
        return None


def save_profile_db(profile: UserProfile) -> bool:
    db = _get_db()
    if not db:
        return False
    try:
        doc = {"user_id": profile.user_id, "name": profile.name, "occupation": profile.occupation, "financial_goals": profile.financial_goals, "risk_tolerance": profile.risk_tolerance, "cash_balance": profile.assets.cash_balance, "savings": profile.assets.savings, "investments": profile.assets.investments, "liabilities": profile.assets.liabilities, "monthly_income": profile.monthly_income, "monthly_expenses": profile.monthly_expenses, "notes": profile.notes, "updated_at": datetime.now(timezone.utc)}
        db["user_profiles"].update_one({"user_id": profile.user_id}, {"$set": doc}, upsert=True)
        return True
    except Exception:
        return False


def get_chat_history_db(user_id: str, limit: int = 50) -> list[dict]:
    db = _get_db()
    if not db:
        return []
    try:
        cursor = db["chat_history"].find({"user_id": user_id}, {"_id": 0, "role": 1, "content": 1}).sort("created_at", -1).limit(limit)
        results = list(cursor)
        results.reverse()
        return results
    except Exception:
        return []


def save_message_db(user_id: str, role: str, content: str) -> bool:
    db = _get_db()
    if not db:
        return False
    try:
        db["chat_history"].insert_one({"user_id": user_id, "role": role, "content": content, "created_at": datetime.now(timezone.utc)})
        return True
    except Exception:
        return False


def clear_history_db(user_id: str) -> bool:
    db = _get_db()
    if not db:
        return False
    try:
        db["chat_history"].delete_many({"user_id": user_id})
        return True
    except Exception:
        return False
