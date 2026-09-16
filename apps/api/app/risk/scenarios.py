from app.domain.models import MarketSnapshot, ScenarioPoint


def build_scenarios(amount: float, market: MarketSnapshot, horizon_days: int) -> list[ScenarioPoint]:
    horizon_scale = max(horizon_days / 30, 0.25) ** 0.5
    base_vol = max(market.volatility_30d, 0.08) * horizon_scale
    trend = max(min(market.day_change_percent / 100, 0.04), -0.04) * min(horizon_days / 14, 2)
    execution_drag = 0.003 if "KASE" in market.exchange or "MOEX" in market.exchange else 0.0015
    moves = [-1.45, -0.85, -0.3, 0.2, 0.75, 1.35]
    weights = [0.08, 0.17, 0.25, 0.25, 0.17, 0.08]
    labels = ["Stress", "Bad", "Soft loss", "Base gain", "Good", "Strong"]

    scenarios: list[ScenarioPoint] = []
    for label, move, weight in zip(labels, moves, weights):
        outcome = ((move * base_vol) + trend - execution_drag) * 100
        projected = amount * (1 + outcome / 100)
        scenarios.append(
            ScenarioPoint(
                label=label,
                outcome_percent=round(outcome, 2),
                projected_value=round(projected, 2),
                probability_weight=weight,
            )
        )
    return scenarios
