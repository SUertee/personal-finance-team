"""
app.py - FastAPI entrypoint for the Finance AI Multi-Agent System.
Mounts all route handlers from the api/ package.
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.analyze import router as analyze_router
from api.chat import router as chat_router
from api.health import router as health_router
from api.profile import router as profile_router
from api.transactions import router as transactions_router

app = FastAPI(
    title="Finance AI Multi-Agent System",
    description=(
        "Personal finance analysis system with LangChain multi-agent architecture. "
        "Features: expense analysis, budget analysis, news scouting, "
        "financial advising, and strategic insights."
    ),
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(chat_router)
app.include_router(profile_router)
app.include_router(transactions_router)
