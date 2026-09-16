import pytest

from app.agents.deep_analysis import (
    build_deep_analysis,
    build_opportunity_radar,
    render_deep_analysis_markdown,
)
from app.agents.external_engines import list_external_engines
from app.agents.mandates import list_mandates
from app.agents.prompt_library import list_prompt_templates
from app.agents.review import build_analysis_review_from_market
from app.core.config import settings
from app.domain.models import (
    Currency,
    DeepAnalysisRequest,
    ExpenseItem,
    FinancialProfileRequest,
    MarketSnapshot,
    OpportunityRadarRequest,
)
from app.storage.database import (
    get_deep_analysis_run,
    list_analysis_reviews,
    list_deep_analysis_runs,
    save_analysis_review,
    save_deep_analysis_run,
)


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


def test_external_engine_registry_sees_copied_projects() -> None:
    engines = {engine.name: engine for engine in list_external_engines()}

    assert engines["TradingAgents"].present
    assert engines["TradingAgents"].license == "Apache-2.0"
    assert engines["ai-hedge-fund"].present
    assert engines["ai-hedge-fund"].license == "MIT"


def test_prompt_library_contains_core_agent_team() -> None:
    roles = {prompt.role for prompt in list_prompt_templates()}

    assert "Market Analyst" in roles
    assert "Risk Manager" in roles
    assert "Teacher Agent" in roles
    assert "Pro Opportunity Scout" in roles


def test_agent_mandates_define_retail_and_pro_modes() -> None:
    mandates = {mandate.name: mandate for mandate in list_mandates()}

    assert "retail_learning" in mandates
    assert "pro_opportunity_scout" in mandates
    assert "Pro Opportunity Scout" in mandates["pro_opportunity_scout"].agent_team


@pytest.mark.anyio
async def test_deep_analysis_builds_multi_agent_memo() -> None:
    analysis = await build_deep_analysis(
        DeepAnalysisRequest(
            profile=_profile(),
            symbol="KZTK",
            provider="demo_cis",
            amount=25_000,
            horizon_days=30,
            pro_mode=True,
        )
    )

    roles = {agent.role for agent in analysis.agents}

    assert "Market Analyst" in roles
    assert "Risk Manager" in roles
    assert "Portfolio Manager" in roles
    assert "Pro Opportunity Scout" in roles
    assert analysis.memo.action in {"paper_watch", "small_paper_position", "research_watchlist"}
    assert analysis.debate
    assert analysis.evidence


@pytest.mark.anyio
async def test_deep_analysis_renders_markdown_memo() -> None:
    analysis = await build_deep_analysis(
        DeepAnalysisRequest(
            profile=_profile(),
            symbol="KZTK",
            provider="demo_cis",
            amount=25_000,
            horizon_days=30,
        )
    )
    markdown = render_deep_analysis_markdown(analysis)

    assert "# FInAI Deep Analysis: KZTK" in markdown
    assert "## Agent Findings" in markdown
    assert "## Invalidation Triggers" in markdown


@pytest.mark.anyio
async def test_deep_analysis_run_is_persisted(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "sqlite_path", str(tmp_path / "finai-analysis.sqlite3"))
    analysis = await build_deep_analysis(
        DeepAnalysisRequest(
            profile=_profile(),
            symbol="KZTK",
            provider="demo_cis",
            amount=25_000,
            horizon_days=30,
        )
    )

    save_deep_analysis_run(analysis)
    runs = list_deep_analysis_runs()
    restored = get_deep_analysis_run(analysis.id)

    assert runs[0].id == analysis.id
    assert restored is not None
    assert restored["memo"]["action"] == analysis.memo.action


@pytest.mark.anyio
async def test_deep_analysis_review_marks_and_persists_thesis_progress(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "sqlite_path", str(tmp_path / "finai-review.sqlite3"))
    analysis = await build_deep_analysis(
        DeepAnalysisRequest(
            profile=_profile(),
            symbol="KZTK",
            provider="demo_cis",
            amount=25_000,
            horizon_days=30,
        )
    )
    current_market = MarketSnapshot(
        symbol=analysis.market.symbol,
        provider=analysis.market.provider,
        exchange=analysis.market.exchange,
        currency=analysis.market.currency,
        last_price=analysis.market.last_price * 1.1,
        day_change_percent=1.8,
        volatility_30d=analysis.market.volatility_30d,
        liquidity_note=analysis.market.liquidity_note,
        source_note="Synthetic review test snapshot.",
    )

    review = build_analysis_review_from_market(analysis, current_market)
    save_analysis_review(review)
    reviews = list_analysis_reviews()

    assert review.return_percent == 10
    assert review.thesis_status == "ahead_early"
    assert reviews[0].run_id == analysis.id
    assert reviews[0].thesis_status == review.thesis_status


@pytest.mark.anyio
async def test_opportunity_radar_ranks_candidates() -> None:
    radar = await build_opportunity_radar(
        OpportunityRadarRequest(
            profile=_profile(),
            symbols=["KZTK", "KSPI", "KZTK"],
            provider="demo_cis",
            amount=25_000,
            horizon_days=30,
            max_results=3,
        )
    )

    assert len(radar.candidates) == 2
    assert radar.candidates[0].rank_score >= radar.candidates[-1].rank_score
    assert radar.candidates[0].top_watch_item
