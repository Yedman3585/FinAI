from app.domain.models import Currency, MarketSnapshot
from app.market.providers.base import MarketDataProvider


class DemoCisProvider(MarketDataProvider):
    name = "demo_cis"

    _snapshots = {
        "KSPI": MarketSnapshot(
            symbol="KSPI",
            provider=name,
            exchange="NASDAQ / Kazakhstan-linked ADR",
            currency=Currency.USD,
            last_price=121.4,
            day_change_percent=1.2,
            volatility_30d=0.34,
            liquidity_note="ADR trades globally; local KZT/USD risk still matters.",
            source_note="Demo fixture until live provider keys are connected.",
        ),
        "AAPL": MarketSnapshot(
            symbol="AAPL",
            provider=name,
            exchange="NASDAQ",
            currency=Currency.USD,
            last_price=229.8,
            day_change_percent=-0.4,
            volatility_30d=0.21,
            liquidity_note="High liquidity; currency conversion still affects KZT users.",
            source_note="Demo fixture until yfinance/live provider is connected.",
        ),
        "KZTK": MarketSnapshot(
            symbol="KZTK",
            provider=name,
            exchange="KASE",
            currency=Currency.KZT,
            last_price=36120,
            day_change_percent=0.6,
            volatility_30d=0.27,
            liquidity_note="Local liquidity can be thinner than US mega-cap equities.",
            source_note="Demo fixture for KASE adapter shape.",
        ),
    }

    async def snapshot(self, symbol: str) -> MarketSnapshot:
        ticker = symbol.upper()
        return self._snapshots.get(
            ticker,
            MarketSnapshot(
                symbol=ticker,
                provider=self.name,
                exchange="Demo market",
                currency=Currency.USD,
                last_price=100,
                day_change_percent=0,
                volatility_30d=0.3,
                liquidity_note="Unknown liquidity. Treat as research-only.",
                source_note="Demo fallback snapshot.",
            ),
        )

