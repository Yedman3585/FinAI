from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.domain.models import AnalysisReviewResponse, DeepAnalysisResponse, MarketSnapshot
from app.market.registry import get_provider


async def build_analysis_review(analysis: DeepAnalysisResponse) -> AnalysisReviewResponse:
    current_market = await get_provider(analysis.market.provider).snapshot(analysis.market.symbol)
    return build_analysis_review_from_market(analysis, current_market)


def build_analysis_review_from_market(
    analysis: DeepAnalysisResponse,
    current_market: MarketSnapshot,
) -> AnalysisReviewResponse:
    reviewed_at = datetime.now(timezone.utc)
    days_elapsed = max((_parse_datetime(reviewed_at.isoformat()) - _parse_datetime(analysis.created_at)).days, 0)
    entry_price = analysis.market.last_price
    current_price = current_market.last_price
    return_percent = round((current_price - entry_price) / entry_price * 100, 2) if entry_price else 0
    thesis_status, verdict, learning_note, next_actions = _judge_thesis(
        analysis=analysis,
        return_percent=return_percent,
        days_elapsed=days_elapsed,
    )

    return AnalysisReviewResponse(
        id=str(uuid4()),
        run_id=analysis.id,
        reviewed_at=reviewed_at.isoformat(),
        symbol=analysis.market.symbol,
        provider=analysis.market.provider,
        currency=current_market.currency,
        entry_price=round(entry_price, 4),
        current_price=round(current_price, 4),
        return_percent=return_percent,
        days_elapsed=days_elapsed,
        horizon_days=analysis.horizon_days,
        thesis_status=thesis_status,
        verdict=verdict,
        learning_note=learning_note,
        next_actions=next_actions,
        source_note=current_market.source_note,
    )


def _judge_thesis(
    analysis: DeepAnalysisResponse,
    return_percent: float,
    days_elapsed: int,
) -> tuple[str, str, str, list[str]]:
    action = analysis.memo.action
    horizon_done = days_elapsed >= analysis.horizon_days
    stress = min(point.outcome_percent for point in analysis.scenarios)
    base = next(
        (point.outcome_percent for point in analysis.scenarios if point.label == "Base gain"),
        0,
    )
    invalidation_threshold = min(-12, stress * 0.5)

    if action == "avoid":
        if return_percent > 8:
            return (
                "opportunity_missed",
                "Риск-фильтр спасал бюджет, но рынок ушёл выше. Это не ошибка: нужно понять, какой риск мы отказались брать.",
                "Избежать сделки и пропустить рост может быть рационально, если личный бюджет не выдерживал просадку.",
                ["review risk gate", "compare missed upside with avoided drawdown", "do not chase after the move"],
            )
        return (
            "risk_call_working",
            "Решение не входить выглядит оправданным: рынок не дал достаточного вознаграждения за риск.",
            "Хороший агент должен уметь защищать пользователя от лишнего действия, а не только искать покупки.",
            ["keep cash buffer first", "wait for a cleaner thesis", "review another idea"],
        )

    if return_percent <= invalidation_threshold:
        return (
            "invalidated",
            "Тезис приблизился к зоне поломки: результат хуже допустимого учебного коридора.",
            "Главный урок здесь не в убытке, а в том, сработало ли заранее записанное правило выхода.",
            ["close or freeze paper thesis", "write what evidence was missed", "lower future position size"],
        )

    if not horizon_done:
        if return_percent >= max(base * 0.5, 2):
            return (
                "ahead_early",
                "Идея идёт лучше раннего ожидания, но горизонт ещё не завершён.",
                "Ранняя прибыль не доказывает тезис; она только покупает время для более спокойной проверки.",
                ["avoid increasing size automatically", "refresh evidence", "set next review date"],
            )
        if return_percent >= 0:
            return (
                "on_track",
                "Идея пока внутри нормального учебного коридора.",
                "Нулевой или небольшой плюс полезен, если пользователь учится вести тезис, а не угадывать свечу.",
                ["keep paper tracking", "watch invalidation triggers", "compare against peer ideas"],
            )
        return (
            "behind_but_alive",
            "Идея просела, но ещё не сломала заранее заданный риск-коридор.",
            "Просадка проверяет дисциплину: стоит смотреть на тезис и риск, а не только на неприятный процент.",
            ["check whether thesis changed", "do not average down automatically", "wait for horizon review"],
        )

    if return_percent >= base:
        return (
            "validated",
            "Тезис прошёл горизонт лучше базового сценария.",
            "Теперь важно отделить качество анализа от удачного рыночного шума.",
            ["promote to case study", "record which evidence mattered", "rank against new opportunities"],
        )
    if return_percent >= 0:
        return (
            "partially_validated",
            "Тезис не сломался, но результат слабее базового сценария.",
            "Даже положительный итог может быть слабым, если риск был высоким или деньги можно было использовать лучше.",
            ["review opportunity cost", "tighten catalyst requirement", "compare to watchlist"],
        )
    return (
        "failed",
        "К горизонту тезис дал отрицательный результат и требует разбора ошибок.",
        "Paper-режим ценен именно здесь: пользователь получает опыт без реального финансового ущерба.",
        ["write post-mortem", "identify missed risk", "keep next idea smaller"],
    )


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
