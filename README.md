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
  -> MongoDB-backed profile/chat persistence
```

## Repository Layout

```text
client/      React frontend
server/      FastAPI + LangGraph backend
```

## Prerequisites

- Node.js 20+
- Python 3.12+
- MongoDB 7+ or Docker
- Optional: Ollama or OpenAI credentials for LLM access
- Optional: n8n for workflow experiments

## Environment

### Server

Use `server/.env.example` as the reference for local configuration. The backend supports:

- `LLM_PROVIDER=ollama` with `OLLAMA_BASE_URL` and `OLLAMA_MODEL`
- `LLM_PROVIDER=openai` with `OPENAI_API_KEY` and `OPENAI_MODEL`
- `MONGODB_URI` and `MONGODB_DB`
- optional `NEWS_API_KEY`

### Client

Typical local client variables:

- `VITE_LLM_ENDPOINT=http://localhost:8000/chat`
- `VITE_N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/finance-analyze-pdf`
- any Supabase values required by the dashboard views

## Local Development

### Run the server

```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
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
- `mongo`
- `server`

The `client` service is included as a commented template and can be enabled when needed.

```bash
docker compose up --build
```

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

## Notes on n8n

If you still use n8n in your setup, treat it as an external integration layer around this repository rather than a source directory inside it.
