# GitHub Repositories

## Copied Into This Workspace

These repositories are cloned into `external/` as isolated reference/engine candidates. They are not mixed into the FInAI core package.

### TradingAgents

- Local path: `external/TradingAgents`
- Source: https://github.com/TauricResearch/TradingAgents
- Commit: `be952b8eccb49720509af544c6675233bc1f10d0`
- Commit date: 2026-09-07
- License: Apache-2.0
- Why it matters:
  - Best candidate for multi-agent trading analysis.
  - Strong fit for bull, bear, fundamental, technical, news, and risk roles.
  - Current FInAI `local_multi_agent_v1` mirrors this role model in a lightweight deterministic way.
  - Direct execution should happen in a separate Python 3.12 environment with explicit LLM/data API keys.

### ai-hedge-fund

- Local path: `external/ai-hedge-fund`
- Source: https://github.com/virattt/ai-hedge-fund
- Commit: `fc1bf250ead209ae5f02c39c3d0062c4bb554505`
- Commit date: 2026-09-03
- License: MIT
- Why it matters:
  - Good reference for educational hedge-fund style workflows.
  - Faster inspiration for paper trading and backtesting demos.
  - Strong concepts to reuse: fund mandate, alpha models, risk limits, simulated broker, backtest cycle.

## Evaluated But Not Copied

- https://github.com/ranaroussi/yfinance
  - Quick global market data fallback.
  - Useful for US tickers and Kaspi ADR demos.
  - Used as a Python dependency, not copied as source.

- https://github.com/tradernet/tn.api
  - Official Tradernet API documentation.
  - Important for Freedom/Tradernet-style portfolio and trading workflows.
  - Not copied yet; next best integration when demo/sandbox credentials are ready.

- https://github.com/kutsevol/tradernet-api
  - Python client for Tradernet API.
  - Useful after credentials are ready.

- https://github.com/tradernet-api/tradernet-mcp-codex
  - Codex MCP integration for Tradernet.
  - Useful for smoke tests and portfolio/quotes exploration.

- https://github.com/OpenBB-finance/OpenBB
  - Strong reference for data platform architecture.
  - Avoid copying the whole repo into MVP because it is large and AGPL-licensed.

## Rule

Do not copy a whole repo into FInAI unless it becomes a clearly isolated engine package. Prefer adapters and small integrations over bringing a large external codebase into the product core.
