# Finance AI Full-Stack Assistant

This repository contains a full-stack personal finance assistant built around two main pieces:

- `client/`: a React + Vite dashboard for transaction review, reports, and multi-agent chat
- `server/`: a FastAPI + LangGraph backend for finance analysis, user profiles, and agent orchestration

The primary application is the React client talking to the FastAPI server. n8n can still be integrated externally if needed, but it is no longer represented as a first-class directory in this repository.

## Architecture

```text
client (React/Vite)
  -> /analyze, /chat, /profile on server
  -> optional n8n webhook integration

server (FastAPI/LangGraph)
  -> multi-agent orchestration
  -> transaction enrichment, anomaly detection, summaries
  -> pgvector/PostgreSQL-backed profile/chat persistence
```

## Repository Layout

```text
client/                  React frontend (Vite + TypeScript)
server/
  app.py                 FastAPI entrypoint (mounts routers)
  api/                   Route handlers (analyze, chat, profile, health)
  agents/                LangGraph multi-agent system (5 specialist agents)
  db/                    PostgreSQL persistence (connection, repos, schema.sql)
  models/                Pydantic models (user, chat, analysis)
  services/              Business logic (LLM, categorizer, anomalies, memory)
docker-compose.yml       n8n + pgvector/PostgreSQL + server
```

Each `server/` subfolder has its own `README.md` with detailed documentation.

## Prerequisites

- Node.js 20+
- Python 3.12+
- PostgreSQL 16+ or Docker
- Local Docker database image defaults to `pgvector/pgvector:pg16`
- Optional: Ollama or OpenAI credentials for LLM access
- Optional: n8n for workflow experiments

## Environment

### Server

Use `server/.env.example` as the reference for local configuration. The backend supports:

- `LLM_PROVIDER=ollama` with `OLLAMA_BASE_URL` and `OLLAMA_MODEL`
- `LLM_PROVIDER=openai` with `OPENAI_API_KEY` and `OPENAI_MODEL`
- `POSTGRES_DSN` or `DATABASE_URL`
- default local DSN: `postgresql://personal_finance_user:personal_finance_password@localhost:15432/personal_finance`
- optional `NEWS_API_KEY`

### Client

Typical local client variables:

- `VITE_API_BASE_URL=http://localhost:18000`
- `VITE_LLM_ENDPOINT=http://localhost:18000/chat`
- `VITE_N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/finance-analyze-pdf`
- no Supabase variables are required for the current local Postgres flow

## Local Development

### Run the server

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 18000
```

To import the locally processed statement data into Postgres:

```bash
cd ..
python3 scripts/import_processed_to_postgres.py
```

### Run the client

```bash
cd client
npm install
npm run dev
```

## Docker Compose

The root `docker-compose.yml` provisions:

- `n8n`
- `db` (`pgvector/pgvector:pg16`)
- `server`

The `client` service is included as a commented template and can be enabled when needed.

```bash
docker compose up --build
```

Default local endpoints after compose startup:

- database: `127.0.0.1:15432`
- server: `http://localhost:18000`
- n8n: `http://localhost:5678`
- frontend API base: `http://localhost:18000`

## API Overview

The backend keeps the current public routes:

- `GET /health`
- `GET /schema`
- `POST /analyze`
- `POST /chat`
- `GET /profile/{user_id}`
- `PUT /profile/{user_id}`
- `GET /chat/history/{user_id}`
- `DELETE /chat/history/{user_id}`
- `GET /transactions/{user_id}`
- `GET /analysis-runs/latest/{user_id}`

## Notes on n8n

If you still use n8n in your setup, treat it as an external integration layer around this repository rather than a source directory inside it.
