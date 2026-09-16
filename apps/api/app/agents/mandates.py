from app.domain.models import AgentMandate, RiskMandate


MANDATES = [
    AgentMandate(
        name="retail_learning",
        audience="Retail user learning markets through personal money.",
        objective=(
            "Convert everyday budget and one market idea into a safe paper-trading lesson."
        ),
        allowed_markets=["KASE demo", "KASE Global demo", "MOEX ISS", "Yahoo fallback"],
        agent_team=[
            "Market Analyst",
            "Fundamental Analyst",
            "Macro / FX Analyst",
            "Risk Manager",
            "Portfolio Manager",
            "Teacher Agent",
        ],
        risk=RiskMandate(
            max_single_position_percent=0.2,
            max_monthly_free_cash_percent=0.2,
            allowed_actions=["avoid", "paper_watch", "small_paper_position"],
            review_frequency="daily monitor plus horizon review",
        ),
    ),
    AgentMandate(
        name="pro_opportunity_scout",
        audience="Investor or analyst screening public-market and startup ideas.",
        objective=(
            "Rank ideas before consensus using catalysts, market signals, alternative data, "
            "and explicit evidence gaps."
        ),
        allowed_markets=["KASE", "AIX", "MOEX", "US equities", "startup/private-market watchlist"],
        agent_team=[
            "Market Analyst",
            "Fundamental Analyst",
            "Macro / FX Analyst",
            "Risk Manager",
            "Portfolio Manager",
            "Pro Opportunity Scout",
        ],
        risk=RiskMandate(
            max_single_position_percent=0.1,
            max_monthly_free_cash_percent=0.35,
            allowed_actions=["avoid", "research_watchlist", "paper_watch"],
            review_frequency="daily signal refresh plus weekly investment committee memo",
        ),
    ),
]


def list_mandates() -> list[AgentMandate]:
    return MANDATES
