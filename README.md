# FInAI

FInAI is an AI-powered personal finance and investment decision platform.

The product connects everyday money data with real market context: income, expenses, safe-to-try cash, tickers, news, risk scenarios, and educational explanations. The MVP is focused on real market intelligence and paper trading, not live order execution.

## Clone On A New Computer

Clone the project together with the external research engines:

```bash
git clone --recurse-submodules https://github.com/Yedman3585/FinAI.git
cd FinAI
```

If the repository was cloned without submodules, restore them with:

```bash
git submodule update --init --recursive
```

## Project Structure

```text
apps/api       FastAPI backend for user finance, market data, risk scenarios, agents, mobile sessions
apps/web       Mobile-first React/PWA surface for the hackathon demo
apps/android   Native Android app prototype
packages       Shared API contracts and schemas
docs           Product, architecture, and development notes
outputs        Pitch deck and video artifacts
```

## MVP Flow

1. User enters income and expenses.
2. FInAI calculates a safe-to-try amount.
3. User chooses a ticker and amount.
4. Backend converts the amount into the user's budget currency when needed.
5. Backend fetches market data through a provider adapter.
6. Risk engine creates scenario distribution with volatility, trend, and execution drag.
7. Agent layer produces bull, bear, risk, action, monitor, and teacher explanations.
8. User creates a paper position and tracks what changed.
9. Saved analysis runs can be reviewed later against fresh market data.

## What Works Now

- Mobile-first React/PWA interface with money, idea, agents, and monitor views.
- FastAPI backend with finance summary, FX, market snapshots, scenario generation, and paper positions.
- Multi-agent intelligence layer with deep-analysis memo, debate rounds, scoring, evidence, thesis review loop, and opportunity radar.
- Mobile session endpoint that returns the full phone-ready state in one request.
- Live NBK FX adapter for KZT rates.
- Live MOEX ISS adapter for regional exchange data.
- Yahoo/yfinance adapter with local fallback when Yahoo blocks or returns empty data.
- SQLite persistence for profile snapshots and paper positions.
- Android companion prototype with mobile-session API client, live Analyze button, tabs, and home-screen widget skeleton.
- External research engines cloned under `external/`: TradingAgents and ai-hedge-fund.

## Development

API:

```bash
./scripts/dev-api.sh
```

For a physical Android phone on the same Wi-Fi:

```bash
HOST=0.0.0.0 ./scripts/dev-api.sh
```

Enable file watching only when your machine supports it:

```bash
FINAI_API_RELOAD=1 ./scripts/dev-api.sh
```

Web:

```bash
./scripts/dev-web.sh
```

Agent intelligence demo:

```bash
./scripts/demo-agents.sh
```

Mobile app backend demo:

```bash
./scripts/demo-mobile-session.sh
```

If `node` is not available in your shell, run the VS Code task `Web: run with bundled Node`.

Android:

```bash
cd apps/android
./gradlew assembleDebug
```

If the Gradle wrapper is not generated yet, open `apps/android` in Android Studio and let it sync the project.

## Demo Path

1. Start the API with `./scripts/dev-api.sh`.
2. Start the web app with `./scripts/dev-web.sh`.
3. Open `http://127.0.0.1:5173`.
4. Run `KSPI` through `CIS demo` to show the full user journey.
5. Switch to `MOEX ISS` and `SBER` to show live regional market data.
6. Open a paper position and refresh the paper portfolio.
7. Run `./scripts/demo-mobile-session.sh` to show the one-call Android/PWA backend.
8. Run `./scripts/demo-agents.sh` to show the detailed agent backend and Pro-style opportunity radar.
