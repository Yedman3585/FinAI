# FInAI Development Architecture

## Core Decision

FInAI should be built as a real market intelligence and paper-trading product first, not as a live trading bot.

The MVP must prove that it can work with real market data, especially Kazakhstan and nearby markets, while keeping user money safe through simulation, explanations, and manual-only decisions.

## Product Core

The product has five core layers:

1. User finance layer: income, expenses, recurring payments, free cash, safe-to-try amount.
2. Market data layer: equities, ETFs, FX, bonds, issuer/news context, trading calendars.
3. Simulation layer: scenarios, volatility, drawdown, commissions, currency risk, liquidity risk.
4. Agent layer: bull, bear, fundamental, technical, macro, risk, teacher.
5. Interface layer: mobile-first PWA, native Android companion, chat explanation, paper position tracker, widget.

## Architecture

```text
Frontend
  Mobile-first React / PWA
  Money + idea + agents + monitor views

Backend API
  FastAPI
  Auth, user profile, financial context, scenario API

Data Adapters
  KASE adapter
  AIX adapter
  MOEX ISS / ALGOPACK adapter
  Tradernet / Freedom adapter
  Yahoo Finance adapter
  National Bank KZ FX/news adapter

Data Store
  PostgreSQL for users, instruments, decisions
  TimescaleDB or DuckDB/Parquet for price history
  Redis for cache and background jobs

Workers
  Celery / RQ jobs for market refresh, news refresh, simulations

Agent Engine
  TradingAgents or custom LangGraph orchestration
  Structured outputs saved as decision evidence

Risk Engine
  Monte Carlo
  Scenario comparison
  Paper execution with commission, spread, slippage
```

## Current MVP Implementation

The repository now contains a working thin slice of that architecture:

1. `apps/api` FastAPI backend
   - budget summary and safe-to-try calculation;
   - NBK FX rate endpoint;
   - normalized market snapshots;
   - investment scenario endpoint;
   - mobile-session endpoint for one-call phone state;
   - local multi-agent deep-analysis endpoint;
   - Pro-style opportunity radar endpoint;
   - SQLite-backed paper portfolio.
2. `apps/web` mobile-first React/PWA interface
   - editable income and expense inputs;
   - provider/ticker/horizon controls;
   - scenario distribution chart;
   - deep-analysis memo, action/teacher brief, and thesis review;
   - paper-position creation and portfolio view;
   - market monitor view.
3. `apps/android` native Android companion prototype
   - native phone surface matching the PWA demo logic;
   - home-screen widget skeleton for safe-to-try and market comments.
4. `external` copied research engines
   - TradingAgents for full multi-agent trading research;
   - ai-hedge-fund for mandates, risk limits, backtesting, and simulated broker patterns.

## Market Data Strategy

### Kazakhstan first

KASE:
- Use public KASE pages for demo-visible market prices, risk parameters, trading results, and issuer information where allowed.
- Treat real-time and delayed API feeds as commercial information products requiring agreement/subscription.
- Do not make fragile scraping the core of the product.
- Current MVP keeps KASE represented through the `demo_cis` adapter and documents the integration boundary.

AIX:
- Use public Market Watch for demo exploration if accessible.
- Keep a proper AIX adapter boundary because Market Watch API and FIX/ITCH access are member-oriented.

National Bank of Kazakhstan:
- Use official RSS/XML services for FX rates and central bank news.
- FX risk must be shown whenever user income is in KZT and the asset is USD-denominated.
- Current MVP uses the official RSS rates service for live FX conversion.

### Regional expansion

MOEX:
- Use official ISS API for historical/delayed market data where legally acceptable.
- Use ALGOPACK only if token/subscription is available.
- Keep MOEX isolated as a provider because licensing and geopolitical constraints may affect production use.
- Current MVP includes `moex_iss` for live SBER/GAZP/YDEX-style snapshots.

UZSE:
- Keep as later adapter. Public website has market data, but a stable official public developer API is less clear.

### Global fallback

Yahoo Finance / yfinance:
- Use for US tickers and global demos.
- Good for quick MVP, not enough for a CIS-first product.
- Current MVP keeps a local fallback because Yahoo can rate-limit public requests.

Tradernet / Freedom:
- Use for portfolio, quotes, ticker search, account data, and later paper-to-real bridge.
- Live order placement must be opt-in, confirmation-gated, and outside hackathon MVP.

## Repositories To Use

### Primary engine candidate

TauricResearch/TradingAgents
- Use as the agentic analysis reference or engine.
- Strong fit for bull/bear/fundamental/technical/risk roles.
- Better for structured multi-agent reasoning than building from zero.
- Needs custom data adapters for KASE/AIX/MOEX.
- Copied into `external/TradingAgents` as an isolated reference engine.

### Faster alternative

virattt/ai-hedge-fund
- Easier to start and good for educational/demo positioning.
- Useful for fund/backtest/paper-trading ideas.
- Less ideal as the serious regional market-data backbone.
- Copied into `external/ai-hedge-fund` as an isolated reference engine.

### Market data and broker integration

moexalgo/moexalgo
- Use for MOEX ALGOPACK if API token is available.

tradernet/tn.api
- Official Tradernet API docs.

kutsevol/tradernet-api
- Python client for Tradernet/Freedom style account, orders, ticker info, and quote history.

tradernet-api/tradernet-mcp-codex
- Useful for development smoke tests through Codex, not necessarily a production dependency.

ranaroussi/yfinance
- Use as package for global price history.

OpenBB-finance/OpenBB
- Use as reference or optional data layer, but avoid copying the whole repo into MVP because it is large and AGPL-licensed.

## MVP Scope For One Week

Build the product around one complete path:

1. User enters monthly income and expenses.
2. System calculates safe-to-try amount.
3. User chooses a ticker: KASE Global / AIX / US / MOEX demo route.
4. Backend fetches real market data through provider adapters.
5. Risk engine simulates possible outcomes for the chosen amount.
6. Agent engine produces bull, bear, macro, risk, and teacher explanations.
7. User creates a paper position.
8. Dashboard shows what changed today and why it matters.

## What Not To Build In MVP

- No live order execution.
- No broker custody or account aggregation unless Tradernet credentials are ready.
- No claim that the system predicts the future.
- No generic chatbot without real data.
- No hard dependency on one exchange source.

## Winning Demo

The winning demo should show this:

> I have 100 dollars. I want to buy an asset. FInAI checks my real budget, pulls real market context, simulates risk, explains the decision, and lets me safely track a paper position.

## Pro Version Direction

The future Pro product should not be a louder version of the consumer app. It should become an investor operating system:

- startup and public-market deal sourcing;
- alternative data ingestion;
- founder/company/news/entity graph;
- multi-agent memo generation;
- probability-weighted idea ranking;
- portfolio construction and monitoring;
- integration with tools such as Tradernet/Freedom, internal CRMs, and research workspaces.

Consumer FInAI teaches users through their own money. Pro FInAI helps investors discover and prioritize ideas before consensus forms.
