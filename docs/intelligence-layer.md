# FInAI Intelligence Layer

## Current Objective

The product should not feel like a generic chatbot. The backend must behave like a small investment desk that reads the user's personal context, market context, risk, and learning needs before it produces a decision memo.

## Current Implementation

The current backend includes two intelligence endpoints:

- `POST /api/agents/deep-analysis`
- `POST /api/agents/opportunity-radar`
- `GET /api/agents/prompts`
- `GET /api/agents/mandates`
- `GET /api/agents/runs/{run_id}/memo`
- `GET /api/agents/runs/{run_id}/review`
- `GET /api/agents/reviews`

Both run without external LLM keys through `local_multi_agent_v1`. This is intentional for hackathon reliability. The deterministic layer can later be replaced or augmented by TradingAgents, OpenAI, or another LLM provider without changing the product contract.

## Agent Team

Current agents:

- `Market Analyst`: price move, volatility, provider quality, liquidity note.
- `Fundamental Analyst`: known company theme, moat, catalysts, red flags.
- `Macro / FX Analyst`: currency mismatch between asset and household budget.
- `Risk Manager`: stress scenario, safe-to-try gate, drawdown and liquidity risk.
- `Portfolio Manager`: paper-first action, sizing hint, thesis journal.
- `Teacher Agent`: explains the decision through the user's own money.
- `Pro Opportunity Scout`: ranks the idea for future Pro research workflows.

Each role also has a prompt contract in `apps/api/app/agents/prompt_library.py`: objective, required inputs, output contract, and guardrails.

## Deep Analysis Output

Every analysis returns:

- normalized market snapshot;
- risk scenarios;
- evidence list;
- individual agent findings;
- bull/bear/risk debate rounds;
- decision memo;
- teacher note;
- disclaimer.

Saved runs can also be rendered as markdown memos for an investment-committee or pitch demo workflow.

Saved runs can also be reviewed against a fresh market snapshot. This gives the product an audit loop: the agent writes a thesis, waits for new information, then marks the idea as `on_track`, `ahead_early`, `behind_but_alive`, `invalidated`, `validated`, `failed`, or `opportunity_missed`.

The decision memo includes:

- action;
- conviction score;
- opportunity score;
- risk score;
- position-size hint;
- thesis;
- invalidation triggers;
- learning focus.

## Opportunity Radar

`POST /api/agents/opportunity-radar` takes a watchlist and ranks ideas by:

- conviction score;
- opportunity score;
- risk score;
- action quality;
- top watch item.

This is the first small version of the future Pro flow: it does not claim to know the next winner, but it can prioritize where a human or stronger agent system should spend research time.

## Thesis Review Loop

`GET /api/agents/runs/{run_id}/review` compares a saved deep-analysis run with current market data from the same provider.

The review returns:

- entry price and current price;
- paper return percent;
- days elapsed versus the original horizon;
- thesis status;
- verdict;
- learning note;
- next actions.

This matters for both versions of the product:

- for retail users, it turns paper investing into a learning journal;
- for Pro users, it becomes an evidence log for which signals and agents were useful.

## Mandates

The backend now exposes two product mandates:

- `retail_learning`: safe paper-trading lessons for a retail user.
- `pro_opportunity_scout`: watchlist ranking and investment-committee style research for investors.

This follows the useful pattern from `ai-hedge-fund`: a fund or assistant should have an explicit mandate instead of behaving like a generic chatbot.

## External Engines Copied

### TradingAgents

Path: `external/TradingAgents`

Use:

- full LangGraph multi-agent trading research;
- analyst/researcher/trader/risk/portfolio role structure;
- persistent decision logs and checkpoints;
- future direct integration behind the existing `deep-analysis` endpoint.

Reason for not executing directly inside the MVP API yet:

- it expects a heavier Python 3.12-oriented environment;
- it requires LLM and data API keys for full output;
- direct integration should be isolated from the core FastAPI runtime.

### ai-hedge-fund

Path: `external/ai-hedge-fund`

Use:

- mandate-as-data model;
- alpha model registry;
- backtesting engine;
- simulated broker;
- deterministic risk limits.

Reason for not executing directly yet:

- the most useful short-term value is architectural;
- the next milestone is to adapt its mandate/backtest pattern to FInAI's CIS market providers.

## Next Backend Milestones

1. Add scheduled horizon reviews for saved analysis runs and paper positions.
2. Add a TradingAgents bridge running in a separate env, behind feature flag `FINAI_TRADINGAGENTS_ENABLED`.
3. Add a richer mandate format inspired by ai-hedge-fund:
   - target market;
   - risk budget;
   - rebalance cadence;
   - allowed instruments;
   - max position size.
4. Add authenticated Tradernet/Freedom sandbox adapter for account and quote context.
5. Add news/catalyst ingestion for KASE, AIX, MOEX, NBK, company releases, and local media.
6. Add Pro ranking across startups and public-market instruments using alternative data.

## Safety Boundary

The intelligence layer can recommend:

- research priority;
- paper position;
- review date;
- invalidation rule.

It must not execute live orders until broker auth, encrypted secrets, audit logs, and explicit user confirmation screens exist.
