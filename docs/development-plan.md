# FInAI Development Plan

## First Working Version

Build one complete product path:

1. Enter income and expenses.
2. Calculate safe-to-try amount.
3. Select ticker and amount.
4. Fetch market snapshot from a provider adapter.
5. Simulate risk scenarios.
6. Generate analyst and teacher explanations.
7. Create a paper position.

## Parallel Tracks

Backend:
- Build FastAPI endpoints and provider adapters.
- Keep real trading out of MVP.
- Store structured evidence for every agent answer.

Web:
- Build the hackathon demo as a mobile-first PWA.
- Prioritize phone ergonomics: money, idea, agents, monitor.

Android:
- Build a native companion app.
- Start with watchlist, paper position, thesis review, and market comment.

Market Data:
- Start with Yahoo/global data and demo CIS adapters.
- Add MOEX ISS next because it has the clearest public API path.
- Keep KASE/AIX behind adapter interfaces because production feeds may require agreements.
