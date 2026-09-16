from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.agents.briefing import build_agent_brief
from app.agents.deep_analysis import build_deep_analysis, build_opportunity_radar
from app.agents.review import build_analysis_review
from app.domain.models import (
    AnalysisReviewResponse,
    Currency,
    DeepAnalysisRequest,
    FxRate,
    MarketBriefItem,
    MarketBriefResponse,
    MarketSnapshot,
    MobileActionState,
    MobileSessionRequest,
    MobileSessionResponse,
    OpportunityRadarRequest,
    PaperPosition,
    PortfolioSummary,
)
from app.market.fx import fallback_rate, get_nbk_rate
from app.market.registry import get_provider
from app.storage.database import list_position_rows, row_to_position


async def build_mobile_session(payload: MobileSessionRequest) -> MobileSessionResponse:
    analysis = await build_deep_analysis(
        DeepAnalysisRequest(
            profile=payload.profile,
            symbol=payload.symbol,
            provider=payload.provider,
            amount=payload.amount,
            horizon_days=payload.horizon_days,
            thesis=payload.thesis,
            pro_mode=True,
        )
    )
    review = await build_analysis_review(analysis) if payload.include_review else None
    radar = await build_opportunity_radar(
        OpportunityRadarRequest(
            profile=payload.profile,
            symbols=_watchlist(payload),
            provider=payload.provider,
            amount=payload.amount,
            horizon_days=payload.horizon_days,
            max_results=3,
        )
    )
    portfolio = await build_mobile_portfolio()
    market_brief = await build_mobile_market_brief(payload.provider, _watchlist(payload))
    fx_rate = await _mobile_fx_rate(payload.profile.currency, analysis.market)
    agent_brief = build_agent_brief(analysis.profile_summary, analysis.market, analysis.scenarios)

    return MobileSessionResponse(
        id=str(uuid4()),
        generated_at=datetime.now(timezone.utc).isoformat(),
        mode="mobile_session_v1",
        profile_summary=analysis.profile_summary,
        market=analysis.market,
        fx_rate=fx_rate,
        scenarios=analysis.scenarios,
        agent_brief=agent_brief,
        analysis=analysis,
        review=review,
        radar=radar,
        portfolio=portfolio,
        market_brief=market_brief,
        action_state=_build_action_state(analysis.memo.action, analysis.memo.risk_score),
    )


async def build_mobile_portfolio() -> PortfolioSummary:
    rows = list_position_rows()
    positions: list[PaperPosition] = []

    for row in rows:
        try:
            market = await get_provider(row["provider"]).snapshot(row["symbol"])
        except Exception:
            market = None
        positions.append(row_to_position(row, market))

    entry_value = round(sum(item.amount for item in positions), 2)
    current_value = round(sum(item.current_value for item in positions), 2)
    weighted_percent = (
        round((current_value - entry_value) / entry_value * 100, 2) if entry_value else 0
    )

    return PortfolioSummary(
        positions=positions,
        total_entry_value=entry_value,
        total_current_value=current_value,
        weighted_unrealized_percent=weighted_percent,
        note="Paper portfolio only: tracks learning experiments without sending broker orders.",
    )


async def build_mobile_market_brief(provider: str, symbols: list[str]) -> MarketBriefResponse:
    items: list[MarketBriefItem] = []
    tickers = [symbol.strip().upper() for symbol in symbols if symbol.strip()][:6]

    for ticker in tickers:
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


async def _mobile_fx_rate(
    profile_currency: Currency,
    market: MarketSnapshot,
) -> Optional[FxRate]:
    if profile_currency == market.currency:
        return None
    if profile_currency != Currency.KZT:
        return None
    try:
        return await get_nbk_rate(market.currency)
    except Exception as exc:
        return fallback_rate(market.currency, str(exc))


def _watchlist(payload: MobileSessionRequest) -> list[str]:
    seen: set[str] = set()
    ordered = [payload.symbol] + payload.watchlist
    result: list[str] = []
    for raw_symbol in ordered:
        symbol = raw_symbol.strip().upper()
        if symbol and symbol not in seen:
            seen.add(symbol)
            result.append(symbol)
    return result


def _build_action_state(action: str, risk_score: float) -> MobileActionState:
    if action == "avoid":
        return MobileActionState(
            title="Реальные деньги пока не трогаем",
            primary_label="Понять риск",
            secondary_label="Выбрать другую идею",
            risk_badge="blocked",
            action=action,
            message="Агент считает, что личный бюджет важнее этой рыночной идеи.",
        )
    if action in {"paper_watch", "research_watchlist"}:
        return MobileActionState(
            title="Сначала paper-наблюдение",
            primary_label="Paper-watch",
            secondary_label="Review thesis",
            risk_badge="elevated" if risk_score >= 65 else "watch",
            action=action,
            message="Идея интересна, но ей нужны наблюдение, правила выхода и больше данных.",
        )
    return MobileActionState(
        title="Можно тестировать как paper-position",
        primary_label="Paper-position",
        secondary_label="Review thesis",
        risk_badge="controlled",
        action=action,
        message="Сумма проходит бюджетный фильтр, но приложение всё равно не отправляет реальную сделку.",
    )
