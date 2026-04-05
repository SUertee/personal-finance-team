# agents/

LangGraph multi-agent system for personal finance analysis. The orchestrator routes user messages to specialized agents via a StateGraph.

## Architecture

```
User Message
    |
    v
[Router] ──> determines which agent to use
    |
    v
[Agent Dispatch] ──> runs the selected specialist
    |
    v
[Advisor Review?] ──> optional review for complex queries
    |
    v
[Compose Response] ──> assembles final reply
```

## Files

| File | Description |
|------|-------------|
| `orchestrator.py` | Entry point: builds state, invokes the graph, saves messages |
| `graph.py` | LangGraph `StateGraph` definition: router -> dispatch -> review -> compose |
| `expense_analyst.py` | Analyzes transactions: categorization, anomalies, spending patterns |
| `budget_analyst.py` | Evaluates budget health: income vs expenses, savings rate, health score |
| `advisor.py` | Financial advice: asset allocation, savings strategy, debt management |
| `news_scout.py` | Fetches real news via NewsAPI and provides personalized analysis |
| `insight.py` | Strategic analysis: trends, projections, opportunity assessment |

## Agents

| Agent | Trigger Keywords | Output |
|-------|-----------------|--------|
| `expense_analyst` | spending, expenses, transactions | Category summary, anomalies, recommendations |
| `budget_analyst` | budget, savings, financial health | Health score, savings rate, spending patterns |
| `news_scout` | news, market, economy | Summarized articles with impact ratings |
| `advisor` | advice, invest, strategy | Asset allocation, actionable recommendations |
| `insight` | trends, forecast, projection | 3/6/12 month projections, risk radar |
| `general` | (default fallback) | Conversational response |

## Flow Details

1. **Router**: LLM-based classification that reads user message + profile context and outputs `{"agent": "...", "refined_query": "...", "needs_review": bool}`
2. **Dispatch**: Calls the selected agent's main function
3. **Advisor Review** (conditional): If `needs_review=true` and agent is not already `advisor`/`general`, the advisor adds a brief review note
4. **Compose**: Assembles final reply with optional advisor comment

## Adding a New Agent

1. Create `agents/your_agent.py` with an async main function
2. Add the agent name to the router prompt in `graph.py`
3. Add dispatch logic in `agent_dispatch_node()` in `graph.py`
4. Update the health endpoint agent list in `api/health.py`
