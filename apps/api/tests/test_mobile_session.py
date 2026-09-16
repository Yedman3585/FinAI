import pytest

from app.core.config import settings
from app.domain.models import Currency, ExpenseItem, FinancialProfileRequest, MobileSessionRequest
from app.mobile.session import build_mobile_session
from app.storage.database import list_analysis_reviews, list_deep_analysis_runs, save_analysis_review, save_deep_analysis_run


def _profile() -> FinancialProfileRequest:
    return FinancialProfileRequest(
        monthly_income=500_000,
        currency=Currency.KZT,
        emergency_fund=350_000,
        desired_investment_amount=25_000,
        expenses=[
            ExpenseItem(name="Rent", amount=180_000, category="housing"),
            ExpenseItem(name="Food", amount=120_000, category="food"),
            ExpenseItem(name="Transport", amount=35_000, category="transport"),
        ],
    )


@pytest.mark.anyio
async def test_mobile_session_builds_phone_ready_state(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "sqlite_path", str(tmp_path / "finai-mobile.sqlite3"))
    session = await build_mobile_session(
        MobileSessionRequest(
            profile=_profile(),
            symbol="KZTK",
            provider="demo_cis",
            amount=25_000,
            horizon_days=30,
            thesis="Проверить локальную телеком идею.",
            watchlist=["KSPI", "AAPL", "KZTK"],
        )
    )

    assert session.mode == "mobile_session_v1"
    assert session.market.symbol == "KZTK"
    assert session.agent_brief.action_note
    assert session.analysis.memo.action in {"paper_watch", "small_paper_position", "research_watchlist"}
    assert session.review is not None
    assert session.radar.candidates
    assert session.market_brief.items
    assert session.action_state.primary_label


@pytest.mark.anyio
async def test_mobile_session_persistence_payload_is_saveable(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "sqlite_path", str(tmp_path / "finai-mobile-save.sqlite3"))
    session = await build_mobile_session(
        MobileSessionRequest(
            profile=_profile(),
            symbol="KZTK",
            provider="demo_cis",
            amount=25_000,
            include_review=True,
        )
    )

    save_deep_analysis_run(session.analysis)
    if session.review is not None:
        save_analysis_review(session.review)

    runs = list_deep_analysis_runs()
    reviews = list_analysis_reviews()

    assert runs[0].id == session.analysis.id
    assert reviews[0].run_id == session.analysis.id
