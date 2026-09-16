from app.core.config import settings
from app.domain.models import Currency, MarketSnapshot, PaperPositionCreate
from app.risk.scenarios import build_scenarios
from app.storage.database import create_paper_position, list_position_rows, row_to_position


def test_scenarios_are_ordered_from_stress_to_strong() -> None:
    market = MarketSnapshot(
        symbol="KSPI",
        provider="demo_cis",
        exchange="NASDAQ / Kazakhstan-linked ADR",
        currency=Currency.USD,
        last_price=120,
        day_change_percent=1,
        volatility_30d=0.3,
        liquidity_note="Liquid enough for demo.",
        source_note="Test snapshot.",
    )

    scenarios = build_scenarios(100, market, 30)

    assert len(scenarios) == 6
    assert scenarios[0].projected_value < scenarios[-1].projected_value
    assert round(sum(item.probability_weight for item in scenarios), 6) == 1


def test_paper_position_round_trip(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "sqlite_path", str(tmp_path / "finai-test.sqlite3"))
    market = MarketSnapshot(
        symbol="SBER",
        provider="moex_iss",
        exchange="MOEX TQBR / Сбербанк",
        currency=Currency.RUB,
        last_price=250,
        day_change_percent=0,
        volatility_30d=0.25,
        liquidity_note="Test liquidity.",
        source_note="Test snapshot.",
    )

    created = create_paper_position(
        PaperPositionCreate(symbol="SBER", provider="moex_iss", amount=10_000, thesis="test"),
        market,
    )
    rows = list_position_rows()
    restored = row_to_position(rows[0], market)

    assert created.id == restored.id
    assert restored.quantity == 40
    assert restored.current_value == 10_000
