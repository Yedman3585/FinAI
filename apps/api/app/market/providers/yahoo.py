from app.domain.models import Currency, MarketSnapshot
from app.market.providers.base import MarketDataProvider
from app.market.providers.demo_cis import DemoCisProvider


class YahooFinanceProvider(MarketDataProvider):
    name = "yahoo"

    async def snapshot(self, symbol: str) -> MarketSnapshot:
        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            history = ticker.history(period="35d", auto_adjust=False, raise_errors=True)
            if history.empty:
                raise ValueError(f"No Yahoo Finance data for {symbol}")
        except Exception as exc:
            fallback = await DemoCisProvider().snapshot(symbol)
            return fallback.model_copy(
                update={
                    "provider": self.name,
                    "source_note": (
                        "Yahoo Finance request failed, using local demo fallback: "
                        f"{exc}"
                    ),
                }
            )

        closes = history["Close"].dropna()
        last = float(closes.iloc[-1])
        previous = float(closes.iloc[-2]) if len(closes) > 1 else last
        returns = closes.pct_change().dropna()
        volatility = float(returns.std() * (252**0.5)) if len(returns) > 1 else 0.0

        return MarketSnapshot(
            symbol=symbol.upper(),
            provider=self.name,
            exchange="Yahoo Finance",
            currency=Currency.USD,
            last_price=round(last, 2),
            day_change_percent=round((last - previous) / previous * 100, 2) if previous else 0,
            volatility_30d=round(volatility, 3),
            liquidity_note="Liquidity depends on the exchange behind the Yahoo ticker.",
            source_note="Yahoo Finance public data via yfinance; research/demo use only.",
            as_of=str(closes.index[-1]),
        )
