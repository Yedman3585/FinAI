# Overnight MVP Status

Date: 2026-09-13, Asia/Almaty

## Built

- FastAPI backend with finance, market, scenario, FX, paper portfolio, and mobile-session routes.
- Multi-agent backend with deep-analysis, copied engine registry, saved analysis runs, thesis review loop, and opportunity radar.
- One-call mobile session API for Android/PWA screens.
- SQLite persistence at `data/finai.sqlite3`.
- Mobile-first React/Vite PWA interface with:
  - editable household budget;
  - provider, ticker, amount, and horizon controls;
  - FX-aware safe-to-try comparison;
  - scenario chart;
  - deep-analysis memo, agent action, teacher notes, and thesis review;
  - paper-position creation and portfolio list;
  - market monitor view.
- Live data adapters:
  - National Bank of Kazakhstan FX RSS;
  - MOEX ISS market snapshots and history-derived volatility.
- Fallback adapters:
  - CIS demo fixtures for KSPI, AAPL, KZTK;
  - Yahoo/yfinance fallback to demo snapshots when Yahoo is blocked or empty.
- Android companion prototype:
  - native Compose screen with Idea, Agents, and Monitor tabs;
  - live `POST /api/mobile/session` client;
  - editable API URL for emulator or physical phone;
  - home-screen widget skeleton;
  - API-ready app manifest with internet permission.
- Copied external engines:
  - `external/TradingAgents`, Apache-2.0, commit `be952b8eccb49720509af544c6675233bc1f10d0`;
  - `external/ai-hedge-fund`, MIT, commit `fc1bf250ead209ae5f02c39c3d0062c4bb554505`.

## Verified

- Web production build passes.
- API imports successfully.
- Backend tests pass: 15 passed.
- Agent tests pass: deep analysis, thesis review loop, opportunity radar, copied engine registry.
- Local API health endpoint returns OK.
- NBK USD/KZT endpoint returned a live rate.
- MOEX `SBER` snapshot returned live exchange data.
- Paper-position creation and list endpoints work.
- Web dev server returns HTTP 200.

## Known Limits

- No live broker order placement. This is intentional for MVP safety.
- Android APK was not built in this environment because Gradle and Android SDK are not installed.
- Yahoo Finance may rate-limit public calls; the provider is resilient but not a primary CIS data source.
- KASE automated API access likely requires subscription/agreement. MVP keeps KASE as a clean adapter boundary and demo fixture.
- Browser-based visual QA for `127.0.0.1:5173` was blocked by the Codex browser tool policy, so UI verification used TypeScript build and HTTP checks.

## Next Best Steps

1. Generate Android Gradle wrapper after opening `apps/android` in Android Studio.
2. Add authenticated Tradernet/Freedom sandbox adapter for account and quote workflows.
3. Add a feature-flagged bridge that runs TradingAgents in its own Python 3.12 environment.
4. Add ai-hedge-fund-style mandate/backtest cycle on top of FInAI market providers.
5. Add scheduled automatic review jobs for saved theses after their horizon expires.
6. Add user login and encrypted secrets store before connecting any broker credentials.
7. Replace KASE demo fixture with subscription-backed market data once access is available.
