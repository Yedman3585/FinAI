import pytest

from app.agents.deep_analysis import build_deep_analysis
from app.domain.models import Currency, DeepAnalysisRequest, ExpenseItem, FinancialProfileRequest, FxRate


@pytest.mark.anyio
async def test_deep_analysis_blocks_when_budget_has_no_free_cash() -> None:
    profile = FinancialProfileRequest(
        monthly_income=300_000,
        currency=Currency.KZT,
        emergency_fund=50_000,
        desired_investment_amount=50_000,
        expenses=[
            ExpenseItem(name="Rent", amount=180_000, category="housing"),
            ExpenseItem(name="Food", amount=120_000, category="food"),
            ExpenseItem(name="Debt", amount=40_000, category="debt"),
        ],
    )

    analysis = await build_deep_analysis(
        DeepAnalysisRequest(
            profile=profile,
            symbol="KZTK",
            provider="demo_cis",
            amount=50_000,
            horizon_days=30,
        )
    )

    assert analysis.profile_summary.status == "risk_blocked"
    assert analysis.memo.action == "avoid"
    assert analysis.memo.risk_score >= 70


@pytest.mark.anyio
async def test_fx_mismatch_pushes_usd_asset_to_paper_watch(monkeypatch) -> None:
    profile = FinancialProfileRequest(
        monthly_income=500_000,
        currency=Currency.KZT,
        emergency_fund=250_000,
        desired_investment_amount=100,
        expenses=[
            ExpenseItem(name="Rent", amount=180_000, category="housing"),
            ExpenseItem(name="Food", amount=120_000, category="food"),
            ExpenseItem(name="Transport", amount=35_000, category="transport"),
            ExpenseItem(name="Subscriptions", amount=15_000, category="subscriptions"),
        ],
    )

    async def fake_rate(base: Currency) -> FxRate:
        return FxRate(
            base=base,
            rate=450,
            source_note="Test FX rate.",
        )

    monkeypatch.setattr("app.agents.deep_analysis.get_nbk_rate", fake_rate)

    analysis = await build_deep_analysis(
        DeepAnalysisRequest(
            profile=profile,
            symbol="KSPI",
            provider="demo_cis",
            amount=100,
            horizon_days=30,
        )
    )

    assert analysis.market.currency == Currency.USD
    assert analysis.profile_summary.status == "cautious"
    assert analysis.memo.action == "paper_watch"
    assert analysis.memo.risk_score >= 65
