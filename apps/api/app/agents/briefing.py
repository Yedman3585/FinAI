from app.domain.models import AgentBrief, FinancialProfileSummary, MarketSnapshot, ScenarioPoint


def build_agent_brief(
    profile: FinancialProfileSummary,
    market: MarketSnapshot,
    scenarios: list[ScenarioPoint],
) -> AgentBrief:
    worst = min(scenarios, key=lambda item: item.projected_value)
    best = max(scenarios, key=lambda item: item.projected_value)

    bull_case = [
        f"В сильном сценарии {market.symbol} может дать около {best.outcome_percent}% за горизонт.",
        "Paper tracking превращает интерес к рынку в обучающий цикл без реального приказа брокеру.",
    ]
    bear_case = [
        f"В стресс-сценарии позиция падает примерно до {worst.projected_value} в валюте актива.",
        f"Для пользователя с бюджетом в {profile.currency} важен не только тикер, но и валютный риск.",
    ]
    risk_case = [
        market.liquidity_note,
        "Историческая волатильность не обещает такой же будущий результат.",
        "Safe-to-try сумма должна быть отдельно от аренды, долгов и базовых расходов.",
    ]
    teacher_note = (
        "Смысл не в том, чтобы угадать рынок. Смысл в том, чтобы увидеть диапазон "
        "исходов и понять, какая часть риска связана с активом, валютой и личным бюджетом."
    )
    if profile.status == "risk_blocked":
        action_note = "Не открывать даже paper-position как инвестиционный сигнал; сначала восстановить бюджет."
        risk_level = "high"
    elif profile.status == "cautious" or market.volatility_30d > 0.45:
        action_note = "Открывать только учебную paper-position и уменьшить сумму до safe-to-try лимита."
        risk_level = "elevated"
    else:
        action_note = "Можно открыть учебную paper-position и поставить ее на ежедневный мониторинг."
        risk_level = "moderate"

    monitoring_note = (
        f"Сегодня смотреть: изменение {market.day_change_percent}%, волатильность 30d "
        f"{round(market.volatility_30d * 100, 1)}%, источник: {market.provider}."
    )

    return AgentBrief(
        bull_case=bull_case,
        bear_case=bear_case,
        risk_case=risk_case,
        teacher_note=teacher_note,
        action_note=action_note,
        risk_level=risk_level,
        monitoring_note=monitoring_note,
        disclaimer="Educational paper-trading output only. Not investment advice.",
    )
