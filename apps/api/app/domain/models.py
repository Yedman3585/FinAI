from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Currency(str, Enum):
    KZT = "KZT"
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


class ExpenseItem(BaseModel):
    name: str
    amount: float = Field(ge=0)
    category: str = "other"
    recurring: bool = True


class FinancialProfileRequest(BaseModel):
    monthly_income: float = Field(gt=0)
    currency: Currency = Currency.KZT
    expenses: list[ExpenseItem]
    emergency_fund: float = Field(default=0, ge=0)
    desired_investment_amount: float = Field(default=100, ge=0)


class FinancialProfileSummary(BaseModel):
    monthly_income: float
    currency: Currency
    total_expenses: float
    free_cash: float
    safe_to_try_amount: float
    status: str
    notes: list[str]


class StoredProfileSnapshot(BaseModel):
    created_at: str
    request: FinancialProfileRequest
    summary: FinancialProfileSummary


class MarketSnapshot(BaseModel):
    symbol: str
    provider: str
    exchange: str
    currency: Currency
    last_price: float
    day_change_percent: float
    volatility_30d: float
    liquidity_note: str
    source_note: str
    as_of: Optional[str] = None


class FxRate(BaseModel):
    base: Currency
    quote: Currency = Currency.KZT
    rate: float
    change: float = 0
    as_of: Optional[str] = None
    provider: str = "nbk"
    source_note: str


class ScenarioPoint(BaseModel):
    label: str
    outcome_percent: float
    projected_value: float
    probability_weight: float


class AgentBrief(BaseModel):
    bull_case: list[str]
    bear_case: list[str]
    risk_case: list[str]
    teacher_note: str
    action_note: str
    risk_level: str
    monitoring_note: str
    disclaimer: str


class EvidenceItem(BaseModel):
    source: str
    title: str
    detail: str
    weight: float = Field(default=0.5, ge=0, le=1)
    url: Optional[str] = None


class AgentFinding(BaseModel):
    role: str
    stance: str
    score: float = Field(ge=-100, le=100)
    confidence: float = Field(ge=0, le=1)
    summary: str
    evidence: list[str]
    watch_items: list[str]


class DebateRound(BaseModel):
    question: str
    bull_response: str
    bear_response: str
    risk_response: str


class DecisionMemo(BaseModel):
    action: str
    conviction_score: float = Field(ge=0, le=100)
    opportunity_score: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=100)
    position_size_hint: str
    thesis: str
    invalidation_triggers: list[str]
    learning_focus: list[str]


class DeepAnalysisRequest(BaseModel):
    profile: FinancialProfileRequest
    symbol: str = "KSPI"
    provider: str = "demo_cis"
    amount: float = Field(default=100, gt=0)
    horizon_days: int = Field(default=30, ge=7, le=365)
    thesis: str = "Хочу проверить идею на paper-position."
    pro_mode: bool = False


class DeepAnalysisResponse(BaseModel):
    id: str
    created_at: str
    analysis_mode: str
    horizon_days: int = Field(default=30, ge=7, le=365)
    profile_summary: FinancialProfileSummary
    market: MarketSnapshot
    scenarios: list[ScenarioPoint]
    evidence: list[EvidenceItem]
    agents: list[AgentFinding]
    debate: list[DebateRound]
    memo: DecisionMemo
    teacher_note: str
    disclaimer: str


class DeepAnalysisRunSummary(BaseModel):
    id: str
    created_at: str
    symbol: str
    provider: str
    action: str
    conviction_score: float
    risk_score: float


class RenderedMemo(BaseModel):
    id: str
    markdown: str


class AnalysisReviewResponse(BaseModel):
    id: str
    run_id: str
    reviewed_at: str
    symbol: str
    provider: str
    currency: Currency
    entry_price: float
    current_price: float
    return_percent: float
    days_elapsed: int
    horizon_days: int
    thesis_status: str
    verdict: str
    learning_note: str
    next_actions: list[str]
    source_note: str


class AnalysisReviewSummary(BaseModel):
    id: str
    run_id: str
    reviewed_at: str
    symbol: str
    provider: str
    thesis_status: str
    return_percent: float


class OpportunityRadarRequest(BaseModel):
    profile: FinancialProfileRequest
    symbols: list[str] = Field(default_factory=lambda: ["KSPI", "KZTK", "AAPL"])
    provider: str = "demo_cis"
    amount: float = Field(default=100, gt=0)
    horizon_days: int = Field(default=30, ge=7, le=365)
    max_results: int = Field(default=5, ge=1, le=20)


class OpportunityCandidate(BaseModel):
    symbol: str
    provider: str
    action: str
    conviction_score: float
    opportunity_score: float
    risk_score: float
    rank_score: float
    thesis: str
    top_watch_item: str


class OpportunityRadarResponse(BaseModel):
    analysis_mode: str
    candidates: list[OpportunityCandidate]
    note: str


class ExternalEngineStatus(BaseModel):
    name: str
    present: bool
    path: str
    license: str
    role: str
    integration_status: str


class AgentPromptTemplate(BaseModel):
    role: str
    objective: str
    inputs: list[str]
    output_contract: list[str]
    guardrails: list[str]


class RiskMandate(BaseModel):
    max_single_position_percent: float = Field(ge=0, le=1)
    max_monthly_free_cash_percent: float = Field(ge=0, le=1)
    allowed_actions: list[str]
    review_frequency: str


class AgentMandate(BaseModel):
    name: str
    audience: str
    objective: str
    allowed_markets: list[str]
    agent_team: list[str]
    risk: RiskMandate


class InvestmentScenarioRequest(BaseModel):
    profile: FinancialProfileRequest
    symbol: str = "NVDA"
    provider: str = "demo_cis"
    amount: float = Field(default=100, gt=0)
    horizon_days: int = Field(default=30, ge=7, le=365)


class InvestmentScenarioResponse(BaseModel):
    profile_summary: FinancialProfileSummary
    market: MarketSnapshot
    scenarios: list[ScenarioPoint]
    agent_brief: AgentBrief


class PaperPositionCreate(BaseModel):
    symbol: str = "KSPI"
    provider: str = "demo_cis"
    amount: float = Field(gt=0)
    thesis: str = "Учебная paper position"


class PaperPosition(BaseModel):
    id: str
    symbol: str
    provider: str
    exchange: str
    currency: Currency
    amount: float
    quantity: float
    entry_price: float
    current_price: float
    current_value: float
    unrealized_percent: float
    status: str
    thesis: str
    created_at: str
    source_note: str


class PortfolioSummary(BaseModel):
    positions: list[PaperPosition]
    total_entry_value: float
    total_current_value: float
    weighted_unrealized_percent: float
    note: str


class MarketBriefItem(BaseModel):
    title: str
    body: str
    priority: str = "medium"


class MarketBriefResponse(BaseModel):
    provider: str
    items: list[MarketBriefItem]
    symbols: list[str]


class MobileSessionRequest(BaseModel):
    profile: FinancialProfileRequest
    symbol: str = "KSPI"
    provider: str = "demo_cis"
    amount: float = Field(default=100, gt=0)
    horizon_days: int = Field(default=30, ge=7, le=365)
    thesis: str = "Хочу проверить идею на paper-position."
    watchlist: list[str] = Field(default_factory=lambda: ["KSPI", "KZTK", "AAPL"])
    include_review: bool = True


class MobileActionState(BaseModel):
    title: str
    primary_label: str
    secondary_label: str
    risk_badge: str
    action: str
    message: str


class MobileSessionResponse(BaseModel):
    id: str
    generated_at: str
    mode: str
    profile_summary: FinancialProfileSummary
    market: MarketSnapshot
    fx_rate: Optional[FxRate] = None
    scenarios: list[ScenarioPoint]
    agent_brief: AgentBrief
    analysis: DeepAnalysisResponse
    review: Optional[AnalysisReviewResponse] = None
    radar: OpportunityRadarResponse
    portfolio: PortfolioSummary
    market_brief: MarketBriefResponse
    action_state: MobileActionState
