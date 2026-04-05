# services/

Business logic layer: LLM integration, transaction processing, external APIs, and state management.

## Files

| File | Description |
|------|-------------|
| `llm.py` | LLM factory (`get_llm`) supporting Ollama and OpenAI, plus `llm_json_reply` helper |
| `categorizer.py` | Deterministic regex-based transaction categorization with confidence scores |
| `anomalies.py` | Statistical + rule-based anomaly detection (large expenses, fees, new merchants) |
| `summaries.py` | Builds category/month/merchant summary structures for the frontend |
| `news_api.py` | NewsAPI.org client for fetching financial news |
| `schema.py` | JSON Schema definition for the `/analyze` response format |
| `memory.py` | Conversation memory with in-memory cache + PostgreSQL persistence |
| `user_store.py` | User profile management with in-memory cache + PostgreSQL persistence |

## LLM Configuration

Set via environment variables:

```bash
# Ollama (default)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

## Transaction Categorization

`categorizer.py` uses regex rules to classify transactions into:

| Category | Example Patterns |
|----------|-----------------|
| groceries | coles, woolworths, aldi |
| transport | uber, opal, train |
| dining | cafe, restaurant, bar |
| utilities | electric, internet, telstra |
| housing | rent, mortgage, strata |
| fees_interest | fee, interest, charge |
| transfer | transfer, payid |
| other | (fallback) |

Each match returns a confidence score (0.85 for rule match, 0.30 for fallback).

## Anomaly Detection

`anomalies.py` detects three types:

- **large_expense**: Amount exceeds `max(200, mean * 4)`
- **fee_interest**: Regex match on fee/interest keywords
- **new_merchant_spend**: First-time merchant with spend >= $50
