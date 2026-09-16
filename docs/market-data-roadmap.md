# Market Data Roadmap

## Principle

FInAI must feel real because it uses real market context. The MVP can use demo fixtures where access is blocked, but the architecture must make those fixtures replaceable by proper providers.

## Provider Priority

1. National Bank of Kazakhstan FX
   - Live in the current MVP through official RSS/XML rates.
   - Critical for translating USD/RUB/EUR ideas into a KZT household budget.

2. MOEX ISS
   - Live in the current MVP through the public ISS interface.
   - Good for proving real regional exchange adapters.
   - Current adapter normalizes price, day change, 30d volatility, turnover, and trade count.

3. KASE
   - Strategically important for Kazakhstan.
   - Public website pages expose current/T-2 market-price tables.
   - Automated API delivery is positioned by KASE as an information product/subscription path.
   - MVP should keep a clean adapter boundary and avoid fragile scraping as the core.

4. Tradernet / Freedom
   - Best bridge to brokerage workflows.
   - Requires account/API keys.
   - Do not use live order placement in MVP.

5. AIX
   - Strategically important for Kazakhstan-linked products.
   - Keep adapter boundary ready.

6. Yahoo Finance / yfinance
   - Useful for US/global demos.
   - In this environment, Yahoo may rate-limit or return empty data, so the provider has a demo fallback.
   - Good for quick exploration, not enough for a CIS-first product.

## Adapter Contract

Every market provider should return:

- normalized symbol
- exchange
- currency
- last price
- day change
- 30 day volatility
- liquidity note
- source note

Current implementation:

- `demo_cis`: stable hackathon fixture for KSPI, AAPL, and KZTK.
- `moex_iss`: live public MOEX ISS adapter.
- `yahoo`: yfinance adapter with local fallback.
- `nbk`: live National Bank of Kazakhstan FX adapter.

## Source Notes

- NBK RSS services: https://nationalbank.kz/ru/page/RSS
- MOEX ISS documentation: https://www.moex.com/a2920
- KASE market prices: https://kase.kz/en/information/market-prices
- KASE delayed market data: https://kase.kz/en/information/delayed-trade-information

The risk engine and agent engine should never depend on provider-specific response shapes.
