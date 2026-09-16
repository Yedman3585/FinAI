from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from app.domain.finance import summarize_profile
from app.domain.models import (
    AgentFinding,
    Currency,
    DebateRound,
    DecisionMemo,
    DeepAnalysisRequest,
    DeepAnalysisResponse,
    EvidenceItem,
    FinancialProfileSummary,
    FxRate,
    MarketSnapshot,
    OpportunityCandidate,
    OpportunityRadarRequest,
    OpportunityRadarResponse,
    ScenarioPoint,
)
from app.market.fx import fallback_rate, get_nbk_rate
from app.market.registry import get_provider
from app.risk.scenarios import build_scenarios


ASSET_KNOWLEDGE = {
    "KSPI": {
        "name": "Kaspi.kz",
        "theme": "Kazakhstan fintech, payments, marketplace, super-app behaviour.",
        "moat": "Сильная пользовательская привычка, платежная сеть и merchant ecosystem.",
        "catalysts": ["рост digital payments", "кредитное качество", "международная экспансия"],
        "red_flags": ["регуляторный риск", "качество кредитного портфеля", "USD/KZT для KZT-инвестора"],
    },
    "AAPL": {
        "name": "Apple",
        "theme": "Global consumer technology and services ecosystem.",
        "moat": "Бренд, installed base и высокая монетизация сервисов.",
        "catalysts": ["services revenue", "AI-device cycle", "capital returns"],
        "red_flags": ["valuation risk", "China exposure", "slower hardware replacement cycle"],
    },
    "NVDA": {
        "name": "NVIDIA",
        "theme": "AI compute infrastructure and accelerated data-center demand.",
        "moat": "GPU ecosystem, CUDA lock-in and hyperscaler demand.",
        "catalysts": ["data-center capex", "new chip cycle", "software stack expansion"],
        "red_flags": ["cycle risk", "export controls", "very high expectations"],
    },
    "KZTK": {
        "name": "Kazakhtelecom",
        "theme": "Local telecom infrastructure and Kazakhstan dividend story.",
        "moat": "Инфраструктурная позиция и локальный масштаб.",
        "catalysts": ["дивиденды", "asset restructuring", "local connectivity demand"],
        "red_flags": ["низкая ликвидность", "регуляторика", "corporate governance"],
    },
    "SBER": {
        "name": "Sber",
        "theme": "Large Russian bank and ecosystem exposure.",
        "moat": "Масштаб клиентской базы, платежи, кредитование и ecosystem services.",
        "catalysts": ["ставки", "маржа", "дивиденды", "retail credit cycle"],
        "red_flags": ["санкции", "RUB/KZT currency risk", "country concentration"],
    },
    "GAZP": {
        "name": "Gazprom",
        "theme": "Energy, gas exports and regulated domestic market.",
        "moat": "Инфраструктурная монополия и ресурсная база.",
        "catalysts": ["energy prices", "pipeline volumes", "domestic tariffs"],
        "red_flags": ["geopolitics", "capex load", "dividend uncertainty"],
    },
    "YDEX": {
        "name": "Yandex",
        "theme": "Search, ads, mobility, cloud and local tech ecosystem.",
        "moat": "Продуктовая экосистема и сильная локальная data/AI позиция.",
        "catalysts": ["ad market", "cloud/AI services", "mobility economics"],
        "red_flags": ["регуляторика", "valuation risk", "market concentration"],
    },
}


def _clamp(value: float, low: float = 0, high: float = 100) -> float:
    return round(min(max(value, low), high), 2)


async def build_deep_analysis(payload: DeepAnalysisRequest) -> DeepAnalysisResponse:
    market = await get_provider(payload.provider).snapshot(payload.symbol)
    fx_rate = await _fx_for_profile(payload.profile.currency, market)
    desired_amount = _amount_in_profile_currency(payload.amount, payload.profile.currency, market, fx_rate)
    profile_request = payload.profile.model_copy(update={"desired_investment_amount": desired_amount})
    profile = summarize_profile(profile_request)
    scenarios = build_scenarios(payload.amount, market, payload.horizon_days)
    evidence = _build_evidence(profile, market, scenarios, fx_rate)
    agents = _build_agents(profile, market, scenarios, fx_rate, payload.pro_mode)
    memo = _build_memo(payload, profile, market, scenarios, agents, fx_rate)
    debate = _build_debate(profile, market, scenarios, memo)
    teacher_note = _build_teacher_note(profile, market, memo)

    return DeepAnalysisResponse(
        id=str(uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        analysis_mode="local_multi_agent_v1",
        horizon_days=payload.horizon_days,
        profile_summary=profile,
        market=market,
        scenarios=scenarios,
        evidence=evidence,
        agents=agents,
        debate=debate,
        memo=memo,
        teacher_note=teacher_note,
        disclaimer="Educational paper-trading analysis only. Not investment advice.",
    )


async def build_opportunity_radar(payload: OpportunityRadarRequest) -> OpportunityRadarResponse:
    candidates: list[OpportunityCandidate] = []
    seen: set[str] = set()
    for raw_symbol in payload.symbols[:20]:
        symbol = raw_symbol.strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)

        try:
            analysis = await build_deep_analysis(
                DeepAnalysisRequest(
                    profile=payload.profile,
                    symbol=symbol,
                    provider=payload.provider,
                    amount=payload.amount,
                    horizon_days=payload.horizon_days,
                    thesis=f"Pro radar screening for {symbol}.",
                    pro_mode=True,
                )
            )
        except Exception:
            continue

        rank_score = _clamp(
            analysis.memo.conviction_score * 0.42
            + analysis.memo.opportunity_score * 0.43
            - analysis.memo.risk_score * 0.15
        )
        risk_agent = next(
            (agent for agent in analysis.agents if agent.role == "Risk Manager"),
            analysis.agents[0],
        )
        candidates.append(
            OpportunityCandidate(
                symbol=analysis.market.symbol,
                provider=analysis.market.provider,
                action=analysis.memo.action,
                conviction_score=analysis.memo.conviction_score,
                opportunity_score=analysis.memo.opportunity_score,
                risk_score=analysis.memo.risk_score,
                rank_score=rank_score,
                thesis=analysis.memo.thesis,
                top_watch_item=risk_agent.watch_items[0] if risk_agent.watch_items else "review evidence",
            )
        )

    ranked = sorted(candidates, key=lambda item: item.rank_score, reverse=True)[: payload.max_results]
    return OpportunityRadarResponse(
        analysis_mode="local_opportunity_radar_v1",
        candidates=ranked,
        note=(
            "Ranks ideas for research priority only. It is not a buy list and does not execute trades."
        ),
    )


async def _fx_for_profile(profile_currency: Currency, market: MarketSnapshot) -> Optional[FxRate]:
    if profile_currency == market.currency:
        return None
    if profile_currency != Currency.KZT:
        return None
    try:
        return await get_nbk_rate(market.currency)
    except Exception as exc:
        return fallback_rate(market.currency, str(exc))


def _amount_in_profile_currency(
    amount: float,
    profile_currency: Currency,
    market: MarketSnapshot,
    fx_rate: Optional[FxRate],
) -> float:
    if profile_currency == market.currency:
        return amount
    if profile_currency == Currency.KZT and fx_rate is not None:
        return amount * fx_rate.rate
    return amount


def _build_evidence(
    profile: FinancialProfileSummary,
    market: MarketSnapshot,
    scenarios: list[ScenarioPoint],
    fx_rate: Optional[FxRate],
) -> list[EvidenceItem]:
    worst = min(scenarios, key=lambda item: item.projected_value)
    best = max(scenarios, key=lambda item: item.projected_value)
    evidence = [
        EvidenceItem(
            source=market.provider,
            title=f"{market.symbol} normalized market snapshot",
            detail=(
                f"Price {market.last_price} {market.currency}, day change "
                f"{market.day_change_percent}%, 30d volatility {round(market.volatility_30d * 100, 1)}%."
            ),
            weight=0.8,
        ),
        EvidenceItem(
            source="risk_engine",
            title="Scenario distribution",
            detail=f"Worst case {worst.outcome_percent}%, strong case {best.outcome_percent}%.",
            weight=0.75,
        ),
        EvidenceItem(
            source="personal_finance",
            title="Household budget gate",
            detail=(
                f"Free cash {profile.free_cash} {profile.currency}; safe-to-try "
                f"{profile.safe_to_try_amount} {profile.currency}; status {profile.status}."
            ),
            weight=0.9,
        ),
    ]

    if fx_rate is not None:
        evidence.append(
            EvidenceItem(
                source=fx_rate.provider,
                title=f"{fx_rate.base}/{fx_rate.quote} FX conversion",
                detail=f"Rate {fx_rate.rate}, date {fx_rate.as_of or 'n/a'}. {fx_rate.source_note}",
                weight=0.7,
            )
        )

    return evidence


def _build_agents(
    profile: FinancialProfileSummary,
    market: MarketSnapshot,
    scenarios: list[ScenarioPoint],
    fx_rate: Optional[FxRate],
    pro_mode: bool,
) -> list[AgentFinding]:
    knowledge = ASSET_KNOWLEDGE.get(market.symbol, _generic_asset(market.symbol))
    worst = min(scenarios, key=lambda item: item.projected_value)
    best = max(scenarios, key=lambda item: item.projected_value)
    risk_score = _risk_score(profile, market, worst, fx_rate)
    opportunity_score = _opportunity_score(market, worst, best, risk_score)
    technical_score = _clamp(50 + market.day_change_percent * 4 - market.volatility_30d * 18)
    fundamental_score = _clamp(45 + len(knowledge["catalysts"]) * 7 - len(knowledge["red_flags"]) * 4)
    fx_penalty = 12 if fx_rate is not None else 0
    profile_penalty = 20 if profile.status == "cautious" else 35 if profile.status == "risk_blocked" else 0
    source_confidence = _source_confidence(market)

    agents = [
        AgentFinding(
            role="Market Analyst",
            stance=_stance(technical_score),
            score=round(technical_score - 50, 2),
            confidence=source_confidence,
            summary=(
                f"{market.symbol}: short-term move {market.day_change_percent}%, "
                f"volatility {round(market.volatility_30d * 100, 1)}%. "
                "Сигнал полезен для мониторинга, но не является прогнозом."
            ),
            evidence=[
                market.source_note,
                f"Liquidity: {market.liquidity_note}",
            ],
            watch_items=["price change", "volatility spike", "data freshness"],
        ),
        AgentFinding(
            role="Fundamental Analyst",
            stance=_stance(fundamental_score),
            score=round(fundamental_score - 50, 2),
            confidence=0.55 if market.symbol in ASSET_KNOWLEDGE else 0.35,
            summary=f"{knowledge['name']}: {knowledge['theme']} Moat: {knowledge['moat']}",
            evidence=knowledge["catalysts"],
            watch_items=knowledge["red_flags"],
        ),
        AgentFinding(
            role="Macro / FX Analyst",
            stance="cautious" if fx_rate is not None else "neutral",
            score=round(-(fx_penalty + abs(market.day_change_percent) * 0.5), 2),
            confidence=0.72 if fx_rate is not None else 0.45,
            summary=(
                f"Актив в {market.currency}, бюджет в {profile.currency}. "
                "Для пользователя важен итоговый результат после валютного движения."
                if fx_rate is not None
                else "Валюта актива совпадает с валютой бюджета, FX penalty не применяется."
            ),
            evidence=[
                f"FX rate: {fx_rate.rate} {fx_rate.quote} for 1 {fx_rate.base}" if fx_rate else "No FX conversion needed.",
            ],
            watch_items=["central bank rate", "FX volatility", "capital controls"],
        ),
        AgentFinding(
            role="Risk Manager",
            stance="defensive" if risk_score >= 65 else "controlled",
            score=round(50 - risk_score, 2),
            confidence=0.78,
            summary=(
                f"Risk score {risk_score}/100. Stress scenario reaches {worst.projected_value}; "
                f"profile status is {profile.status}."
            ),
            evidence=profile.notes + [f"Worst scenario: {worst.outcome_percent}%"],
            watch_items=["safe-to-try breach", "drawdown", "liquidity gap"],
        ),
        AgentFinding(
            role="Portfolio Manager",
            stance="paper-first" if profile_penalty or risk_score > opportunity_score else "small-test",
            score=round(opportunity_score - risk_score, 2),
            confidence=0.7,
            summary=(
                "Позицию стоит вести как учебный эксперимент: thesis, entry price, invalidation trigger, review date."
            ),
            evidence=[
                f"Opportunity score {opportunity_score}/100",
                f"Risk score {risk_score}/100",
            ],
            watch_items=["position size", "single-name concentration", "review cadence"],
        ),
        AgentFinding(
            role="Teacher Agent",
            stance="explain",
            score=0,
            confidence=0.86,
            summary="Главная учебная задача: отделить рыночный риск от риска личного бюджета.",
            evidence=[
                "same amount feels different before and after FX conversion",
                "probability-weighted scenarios beat one-point predictions",
            ],
            watch_items=["why this thesis can be wrong", "what data changes the decision"],
        ),
    ]

    if pro_mode:
        agents.append(
            AgentFinding(
                role="Pro Opportunity Scout",
                stance="screening",
                score=round(opportunity_score - 50, 2),
                confidence=0.5,
                summary=(
                    "Pro layer should rank this idea against a watchlist using catalysts, abnormal activity, "
                    "funding/news signals, and local liquidity."
                ),
                evidence=[
                    "current MVP has market/FX/scenario signals",
                    "next layer needs news, filings, hiring, founders, GitHub and community data",
                ],
                watch_items=["catalyst calendar", "alternative data", "peer ranking"],
            )
        )

    return agents


def _build_memo(
    payload: DeepAnalysisRequest,
    profile: FinancialProfileSummary,
    market: MarketSnapshot,
    scenarios: list[ScenarioPoint],
    agents: list[AgentFinding],
    fx_rate: Optional[FxRate],
) -> DecisionMemo:
    worst = min(scenarios, key=lambda item: item.projected_value)
    best = max(scenarios, key=lambda item: item.projected_value)
    risk_score = _risk_score(profile, market, worst, fx_rate)
    opportunity_score = _opportunity_score(market, worst, best, risk_score)
    average_confidence = sum(agent.confidence for agent in agents) / len(agents)
    conviction_score = _clamp(40 + (opportunity_score - risk_score) * 0.22 + average_confidence * 35)

    if profile.status == "risk_blocked" or risk_score >= 82:
        action = "avoid"
        size_hint = "Do not allocate money; rebuild cash buffer first."
    elif profile.status == "cautious" or risk_score >= 65:
        action = "paper_watch"
        size_hint = f"Track as paper only; cap real curiosity at {profile.safe_to_try_amount} {profile.currency}."
    elif payload.pro_mode and opportunity_score >= 62:
        action = "research_watchlist"
        size_hint = "Promote to pro watchlist; require more evidence before allocation."
    else:
        action = "small_paper_position"
        size_hint = f"Paper position around {payload.amount} {market.currency}; review after {payload.horizon_days} days."

    knowledge = ASSET_KNOWLEDGE.get(market.symbol, _generic_asset(market.symbol))
    thesis = f"{market.symbol}: {knowledge['theme']} User thesis: {payload.thesis}"

    return DecisionMemo(
        action=action,
        conviction_score=conviction_score,
        opportunity_score=opportunity_score,
        risk_score=risk_score,
        position_size_hint=size_hint,
        thesis=thesis,
        invalidation_triggers=[
            f"Price path approaches stress scenario ({worst.outcome_percent}%).",
            "FX move erases the expected result in the user's home currency.",
            "Liquidity becomes too thin to exit cleanly.",
            "Original thesis no longer matches new evidence.",
        ],
        learning_focus=[
            "volatility versus permanent loss",
            "currency conversion into real household buying power",
            "paper thesis journal before real execution",
        ],
    )


def _build_debate(
    profile: FinancialProfileSummary,
    market: MarketSnapshot,
    scenarios: list[ScenarioPoint],
    memo: DecisionMemo,
) -> list[DebateRound]:
    worst = min(scenarios, key=lambda item: item.projected_value)
    best = max(scenarios, key=lambda item: item.projected_value)

    return [
        DebateRound(
            question="Should the user test this idea now?",
            bull_response=(
                f"Yes as a learning experiment: the strong case reaches {best.projected_value}, "
                "and paper tracking builds market intuition."
            ),
            bear_response=(
                f"Not as a real trade yet: the stress case reaches {worst.projected_value}, "
                "and the user may be above safe-to-try limits."
            ),
            risk_response=f"Decision: {memo.action}. The budget gate beats the market story.",
        ),
        DebateRound(
            question="What would make the system change its mind?",
            bull_response="Better evidence: stronger liquidity, improving trend, and a catalyst tied to the thesis.",
            bear_response="Worse evidence: volatility shock, thesis break, or adverse currency move.",
            risk_response=f"Keep review tied to {profile.currency} buying power, not only the asset chart.",
        ),
    ]


def _build_teacher_note(
    profile: FinancialProfileSummary,
    market: MarketSnapshot,
    memo: DecisionMemo,
) -> str:
    return (
        f"На этом примере пользователь видит три слоя решения: личный бюджет ({profile.currency}), "
        f"рынок ({market.symbol}) и правила выхода. Агент не говорит 'покупай', он превращает идею "
        f"в проверяемый тезис: действие {memo.action}, риск {memo.risk_score}/100, "
        f"conviction {memo.conviction_score}/100."
    )


def render_deep_analysis_markdown(analysis: DeepAnalysisResponse) -> str:
    agent_lines = [
        f"- **{agent.role}** ({agent.stance}, score {agent.score}): {agent.summary}"
        for agent in analysis.agents
    ]
    evidence_lines = [
        f"- **{item.source} / {item.title}**: {item.detail}"
        for item in analysis.evidence
    ]
    debate_lines = [
        (
            f"### {round_index}. {round_item.question}\n"
            f"- Bull: {round_item.bull_response}\n"
            f"- Bear: {round_item.bear_response}\n"
            f"- Risk: {round_item.risk_response}"
        )
        for round_index, round_item in enumerate(analysis.debate, start=1)
    ]
    invalidation_lines = [f"- {item}" for item in analysis.memo.invalidation_triggers]
    learning_lines = [f"- {item}" for item in analysis.memo.learning_focus]

    return "\n\n".join(
        [
            f"# FInAI Deep Analysis: {analysis.market.symbol}",
            f"Run: `{analysis.id}`",
            (
                f"Market: {analysis.market.exchange}, price {analysis.market.last_price} "
                f"{analysis.market.currency}, provider `{analysis.market.provider}`."
            ),
            (
                f"Action: **{analysis.memo.action}**. Conviction "
                f"{analysis.memo.conviction_score}/100, opportunity "
                f"{analysis.memo.opportunity_score}/100, risk {analysis.memo.risk_score}/100."
            ),
            f"## Thesis\n{analysis.memo.thesis}",
            f"## Position Size\n{analysis.memo.position_size_hint}",
            "## Evidence\n" + "\n".join(evidence_lines),
            "## Agent Findings\n" + "\n".join(agent_lines),
            "## Debate\n" + "\n\n".join(debate_lines),
            "## Invalidation Triggers\n" + "\n".join(invalidation_lines),
            "## Learning Focus\n" + "\n".join(learning_lines),
            f"## Teacher Note\n{analysis.teacher_note}",
            f"_{analysis.disclaimer}_",
        ]
    )


def _risk_score(
    profile: FinancialProfileSummary,
    market: MarketSnapshot,
    worst: ScenarioPoint,
    fx_rate: Optional[FxRate],
) -> float:
    profile_penalty = 0
    if profile.status == "cautious":
        profile_penalty = 18
    elif profile.status == "risk_blocked":
        profile_penalty = 38

    currency_penalty = 12 if fx_rate is not None else 0
    liquidity_penalty = 10 if "thin" in market.liquidity_note.lower() or "unknown" in market.liquidity_note.lower() else 4
    drawdown_penalty = min(abs(worst.outcome_percent) * 0.5, 30)
    volatility_penalty = min(market.volatility_30d * 55, 30)
    trend_penalty = min(abs(min(market.day_change_percent, 0)) * 2, 8)

    return _clamp(
        profile_penalty
        + currency_penalty
        + liquidity_penalty
        + drawdown_penalty
        + volatility_penalty
        + trend_penalty
    )


def _opportunity_score(
    market: MarketSnapshot,
    worst: ScenarioPoint,
    best: ScenarioPoint,
    risk_score: float,
) -> float:
    asymmetry = best.outcome_percent - abs(worst.outcome_percent) * 0.42
    trend_bonus = max(min(market.day_change_percent * 3, 12), -12)
    provider_bonus = 8 if _source_confidence(market) >= 0.6 else 2
    return _clamp(50 + asymmetry * 0.45 + trend_bonus + provider_bonus - risk_score * 0.12)


def _stance(score: float) -> str:
    if score >= 62:
        return "bullish"
    if score <= 42:
        return "bearish"
    return "neutral"


def _generic_asset(symbol: str) -> dict[str, Any]:
    return {
        "name": symbol,
        "theme": "Unknown asset; requires external research before any real allocation.",
        "moat": "No verified moat in local knowledge base.",
        "catalysts": ["price action", "market liquidity"],
        "red_flags": ["unknown fundamentals", "unknown governance", "unknown liquidity"],
    }


def _source_confidence(market: MarketSnapshot) -> float:
    source_note = market.source_note.lower()
    if "fallback" in source_note or "demo" in market.provider:
        return 0.48
    if "live" in source_note or market.as_of:
        return 0.66
    return 0.55
