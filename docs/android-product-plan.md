# Android Product Plan

The Android app should be a companion surface, not a smaller copy of the web dashboard.

## Current Direction

The hackathon path is native Android first, mobile-first web/PWA as fallback.

Reason:

- the pitch is stronger when the product runs on the founder's real phone;
- the backend contract is now phone-ready through one endpoint;
- the PWA remains useful if APK installation or device setup fails.

The backend now exposes a phone-ready endpoint:

- `POST /api/mobile/session`

This endpoint returns budget status, selected market, scenarios, deep-analysis memo, thesis review, opportunity radar, paper portfolio, market monitor, and button/action state in one response.

## Android MVP

1. Home screen:
   - free cash
   - safe-to-try amount
   - selected paper position
   - market note of the day

2. Idea tab:
   - API URL
   - ticker/provider
   - amount/horizon
   - thesis
   - live Analyze button
   - market snapshot
   - scenarios

3. Agents tab:
   - thesis review
   - risk manager
   - teacher note
   - portfolio manager
   - opportunity radar

4. Monitor tab:
   - paper portfolio summary
   - market monitor notes

5. Watchlist:
   - selected tickers
   - price change
   - risk level
   - short agent comment

6. Paper position:
   - amount
   - entry price
   - current value
   - what changed since the decision

7. Teacher mode:
   - one simple explanation per market event
   - saved learning notes

8. Home-screen widget:
   - safe-to-try amount
   - market risk color
   - one short comment

## Android Later

- Push notifications for important market changes.
- Offline decision diary.
- Voice question to the finance assistant.
- Broker connection only after explicit user opt-in.
- Biometric lock for portfolio and transaction data.

## API Needs

The app should consume the same backend as web:

- `POST /api/finance/profile`
- `GET /api/markets/{symbol}/snapshot`
- `POST /api/scenarios/investment`
- `POST /api/agents/deep-analysis`
- `GET /api/agents/runs/{run_id}/review`
- `POST /api/agents/opportunity-radar`
- `POST /api/mobile/session`

Avoid Android-only financial logic. Calculations should live in the backend so web and mobile stay consistent.
