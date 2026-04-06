"""
app.py - FastAPI entrypoint for the Finance AI Multi-Agent System.
Mounts all route handlers from the api/ package.
"""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.analyze import router as analyze_router
from api.chat import router as chat_router
from api.health import router as health_router
from api.profile import router as profile_router
from api.transactions import router as transactions_router
from db.connection import close_pool, init_pool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_pool()
    yield
    close_pool()


app = FastAPI(
    title="Finance AI Multi-Agent System",
    description=(
        "Personal finance analysis system with LangChain multi-agent architecture. "
        "Features: expense analysis, budget analysis, news scouting, "
        "financial advising, and strategic insights."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(chat_router)
app.include_router(profile_router)
app.include_router(transactions_router)
