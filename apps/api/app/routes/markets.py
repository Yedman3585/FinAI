from fastapi import APIRouter, HTTPException

from app.domain.models import Currency, FxRate, MarketBriefItem, MarketBriefResponse, MarketSnapshot
from app.market.fx import fallback_rate, get_nbk_rate
from app.market.registry import get_provider, providers

router = APIRouter()


@router.get("/providers")
def list_providers() -> dict[str, list[str]]:
    return {"providers": sorted(providers.keys())}


@router.get("/{symbol}/snapshot", response_model=MarketSnapshot)
async def market_snapshot(symbol: str, provider: str = "demo_cis") -> MarketSnapshot:
    try:
        market_provider = get_provider(provider)
        return await market_provider.snapshot(symbol)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/fx/{base}", response_model=FxRate)
async def fx_rate(base: Currency, fallback: bool = True) -> FxRate:
    try:
        return await get_nbk_rate(base)
    except Exception as exc:
        if fallback:
            return fallback_rate(base, str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/brief", response_model=MarketBriefResponse)
async def market_brief(provider: str = "demo_cis", symbols: str = "KSPI,AAPL,KZTK") -> MarketBriefResponse:
    tickers = [item.strip().upper() for item in symbols.split(",") if item.strip()]
    items: list[MarketBriefItem] = []

    for ticker in tickers[:6]:
        try:
            snapshot = await get_provider(provider).snapshot(ticker)
        except Exception as exc:
            items.append(
                MarketBriefItem(
                    title=f"{ticker}: источник недоступен",
                    body=str(exc),
                    priority="low",
                )
            )
            continue

        priority = "high" if abs(snapshot.day_change_percent) >= 2 else "medium"
        direction = "растет" if snapshot.day_change_percent >= 0 else "снижается"
        items.append(
            MarketBriefItem(
                title=f"{snapshot.symbol} {direction} на {abs(snapshot.day_change_percent)}%",
                body=(
                    f"{snapshot.exchange}: цена {snapshot.last_price} {snapshot.currency}, "
                    f"30d volatility {round(snapshot.volatility_30d * 100, 1)}%. "
                    f"{snapshot.liquidity_note}"
                ),
                priority=priority,
            )
        )

    return MarketBriefResponse(provider=provider, items=items, symbols=tickers)
