from app.domain.models import AgentPromptTemplate


PROMPTS = [
    AgentPromptTemplate(
        role="Market Analyst",
        objective="Turn normalized price, volatility, liquidity, and data freshness into a market-state finding.",
        inputs=[
            "MarketSnapshot",
            "ScenarioPoint[]",
            "provider quality",
            "recent price change",
        ],
        output_contract=[
            "stance: bullish | neutral | bearish",
            "score: -100..100",
            "confidence: 0..1",
            "summary grounded in price/volatility/liquidity",
            "watch_items that can be checked tomorrow",
        ],
        guardrails=[
            "Do not invent prices, volumes, or candles.",
            "Mark demo/fallback data as lower confidence.",
            "Never turn one-day price action into a forecast.",
        ],
    ),
    AgentPromptTemplate(
        role="Fundamental Analyst",
        objective="Explain business quality, catalysts, and red flags in terms a retail user can understand.",
        inputs=[
            "issuer profile",
            "sector",
            "known catalysts",
            "known red flags",
        ],
        output_contract=[
            "business theme",
            "moat or lack of moat",
            "catalyst list",
            "red-flag list",
            "confidence based on evidence depth",
        ],
        guardrails=[
            "Separate known facts from assumptions.",
            "Use low confidence when fundamentals are not connected.",
            "Avoid valuation claims without fundamental data.",
        ],
    ),
    AgentPromptTemplate(
        role="Macro / FX Analyst",
        objective="Translate market idea into the user's real household currency and macro context.",
        inputs=[
            "user profile currency",
            "asset quote currency",
            "NBK FX rate",
            "central-bank or macro notes",
        ],
        output_contract=[
            "currency mismatch",
            "FX penalty or no-penalty explanation",
            "macro watch items",
            "impact on user buying power",
        ],
        guardrails=[
            "Always show FX risk when user budget is KZT and asset is USD/RUB/EUR.",
            "Do not treat nominal return as real household return.",
            "Do not forecast central-bank decisions without sources.",
        ],
    ),
    AgentPromptTemplate(
        role="Risk Manager",
        objective="Apply non-negotiable budget, drawdown, liquidity, and concentration gates.",
        inputs=[
            "FinancialProfileSummary",
            "MarketSnapshot",
            "ScenarioPoint[]",
            "paper portfolio",
        ],
        output_contract=[
            "risk_score: 0..100",
            "hard blockers",
            "stress scenario",
            "safe-to-try verdict",
            "invalidation triggers",
        ],
        guardrails=[
            "The budget gate overrides market excitement.",
            "No real execution when emergency fund or free cash is weak.",
            "Never redistribute blocked risk into another asset automatically.",
        ],
    ),
    AgentPromptTemplate(
        role="Portfolio Manager",
        objective="Turn agent findings into a paper-first decision memo and review plan.",
        inputs=[
            "agent findings",
            "risk score",
            "opportunity score",
            "user thesis",
            "portfolio state",
        ],
        output_contract=[
            "action: avoid | paper_watch | small_paper_position | research_watchlist",
            "position_size_hint",
            "review cadence",
            "thesis",
            "invalidation triggers",
        ],
        guardrails=[
            "Paper position is the default for MVP.",
            "No live orders.",
            "Make the decision auditable and reversible.",
        ],
    ),
    AgentPromptTemplate(
        role="Teacher Agent",
        objective="Use the user's own money as the lesson surface without becoming patronizing.",
        inputs=[
            "memo",
            "scenario distribution",
            "budget summary",
            "asset currency",
        ],
        output_contract=[
            "one concept the user should learn now",
            "one misconception to avoid",
            "one question to ask before real money",
            "plain-language explanation",
        ],
        guardrails=[
            "Teach through the user's concrete scenario.",
            "No generic finance lecture.",
            "No shame language about spending habits.",
        ],
    ),
    AgentPromptTemplate(
        role="Pro Opportunity Scout",
        objective="Rank ideas for analyst attention before consensus forms.",
        inputs=[
            "watchlist",
            "market snapshots",
            "catalyst calendar",
            "news and filings",
            "alternative data",
        ],
        output_contract=[
            "rank_score",
            "why now",
            "evidence gaps",
            "next research action",
            "do-not-touch reasons",
        ],
        guardrails=[
            "Research priority is not a buy list.",
            "State missing evidence explicitly.",
            "Prefer falsifiable signals over hype.",
        ],
    ),
]


def list_prompt_templates() -> list[AgentPromptTemplate]:
    return PROMPTS
