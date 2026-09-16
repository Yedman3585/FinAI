from fastapi import APIRouter, HTTPException

from app.agents.briefing import build_agent_brief
from app.domain.finance import summarize_profile
from app.domain.models import InvestmentScenarioRequest, InvestmentScenarioResponse
from app.market.fx import fallback_rate, get_nbk_rate
from app.market.registry import get_provider
from app.risk.scenarios import build_scenarios
from app.storage.database import save_profile_snapshot

router = APIRouter()


@router.post("/investment", response_model=InvestmentScenarioResponse)
async def investment_scenario(payload: InvestmentScenarioRequest) -> InvestmentScenarioResponse:
    try:
        market = await get_provider(payload.provider).snapshot(payload.symbol)
        desired_amount = payload.amount
        if payload.profile.currency != market.currency:
            if payload.profile.currency.value == "KZT":
                try:
                    fx = await get_nbk_rate(market.currency)
                except Exception as exc:
                    fx = fallback_rate(market.currency, str(exc))
                desired_amount = payload.amount * fx.rate

        profile_request = payload.profile.model_copy(
            update={"desired_investment_amount": desired_amount}
        )
        profile = summarize_profile(profile_request)
        save_profile_snapshot(profile_request, profile)
        scenarios = build_scenarios(payload.amount, market, payload.horizon_days)
        brief = build_agent_brief(profile, market, scenarios)
        return InvestmentScenarioResponse(
            profile_summary=profile,
            market=market,
            scenarios=scenarios,
            agent_brief=brief,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
