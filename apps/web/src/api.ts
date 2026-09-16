export type Currency = "KZT" | "USD" | "EUR" | "RUB";

export type ExpenseItem = {
  name: string;
  amount: number;
  category: string;
  recurring: boolean;
};

export type FinancialProfileRequest = {
  monthly_income: number;
  currency: Currency;
  expenses: ExpenseItem[];
  emergency_fund: number;
  desired_investment_amount: number;
};

export type ProfileSummary = {
  monthly_income: number;
  currency: Currency;
  total_expenses: number;
  free_cash: number;
  safe_to_try_amount: number;
  status: string;
  notes: string[];
};

export type MarketSnapshot = {
  symbol: string;
  provider: string;
  exchange: string;
  currency: Currency;
  last_price: number;
  day_change_percent: number;
  volatility_30d: number;
  liquidity_note: string;
  source_note: string;
  as_of?: string | null;
};

export type ScenarioPoint = {
  label: string;
  outcome_percent: number;
  projected_value: number;
  probability_weight: number;
};

export type AgentBrief = {
  bull_case: string[];
  bear_case: string[];
  risk_case: string[];
  teacher_note: string;
  action_note: string;
  risk_level: string;
  monitoring_note: string;
  disclaimer: string;
};

export type InvestmentScenario = {
  profile_summary: ProfileSummary;
  market: MarketSnapshot;
  scenarios: ScenarioPoint[];
  agent_brief: AgentBrief;
};

export type AgentFinding = {
  role: string;
  stance: string;
  score: number;
  confidence: number;
  summary: string;
  evidence: string[];
  watch_items: string[];
};

export type DebateRound = {
  question: string;
  bull_response: string;
  bear_response: string;
  risk_response: string;
};

export type DecisionMemo = {
  action: string;
  conviction_score: number;
  opportunity_score: number;
  risk_score: number;
  position_size_hint: string;
  thesis: string;
  invalidation_triggers: string[];
  learning_focus: string[];
};

export type DeepAnalysis = {
  id: string;
  created_at: string;
  analysis_mode: string;
  horizon_days: number;
  profile_summary: ProfileSummary;
  market: MarketSnapshot;
  scenarios: ScenarioPoint[];
  evidence: {
    source: string;
    title: string;
    detail: string;
    weight: number;
    url?: string | null;
  }[];
  agents: AgentFinding[];
  debate: DebateRound[];
  memo: DecisionMemo;
  teacher_note: string;
  disclaimer: string;
};

export type AnalysisReview = {
  id: string;
  run_id: string;
  reviewed_at: string;
  symbol: string;
  provider: string;
  currency: Currency;
  entry_price: number;
  current_price: number;
  return_percent: number;
  days_elapsed: number;
  horizon_days: number;
  thesis_status: string;
  verdict: string;
  learning_note: string;
  next_actions: string[];
  source_note: string;
};

export type OpportunityCandidate = {
  symbol: string;
  provider: string;
  action: string;
  conviction_score: number;
  opportunity_score: number;
  risk_score: number;
  rank_score: number;
  thesis: string;
  top_watch_item: string;
};

export type OpportunityRadar = {
  analysis_mode: string;
  candidates: OpportunityCandidate[];
  note: string;
};

export type PaperPosition = {
  id: string;
  symbol: string;
  provider: string;
  exchange: string;
  currency: Currency;
  amount: number;
  quantity: number;
  entry_price: number;
  current_price: number;
  current_value: number;
  unrealized_percent: number;
  status: string;
  thesis: string;
  created_at: string;
  source_note: string;
};

export type PortfolioSummary = {
  positions: PaperPosition[];
  total_entry_value: number;
  total_current_value: number;
  weighted_unrealized_percent: number;
  note: string;
};

export type MarketBriefItem = {
  title: string;
  body: string;
  priority: "low" | "medium" | "high";
};

export type MarketBriefResponse = {
  provider: string;
  items: MarketBriefItem[];
  symbols: string[];
};

export type FxRate = {
  base: Currency;
  quote: Currency;
  rate: number;
  change: number;
  as_of?: string | null;
  provider: string;
  source_note: string;
};

export type MobileSession = {
  id: string;
  generated_at: string;
  mode: string;
  profile_summary: ProfileSummary;
  market: MarketSnapshot;
  fx_rate?: FxRate | null;
  scenarios: ScenarioPoint[];
  agent_brief: AgentBrief;
  analysis: DeepAnalysis;
  review?: AnalysisReview | null;
  radar: OpportunityRadar;
  portfolio: PortfolioSummary;
  market_brief: MarketBriefResponse;
  action_state: {
    title: string;
    primary_label: string;
    secondary_label: string;
    risk_badge: string;
    action: string;
    message: string;
  };
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

function withProfile(profile: FinancialProfileRequest, amount: number) {
  return {
    ...profile,
    desired_investment_amount: amount
  };
}

export const defaultProfile: FinancialProfileRequest = {
  monthly_income: 500000,
  currency: "KZT",
  emergency_fund: 250000,
  desired_investment_amount: 100,
  expenses: [
    { name: "Аренда", amount: 180000, category: "housing", recurring: true },
    { name: "Еда", amount: 120000, category: "food", recurring: true },
    { name: "Транспорт", amount: 35000, category: "transport", recurring: true },
    { name: "Подписки", amount: 15000, category: "subscriptions", recurring: true }
  ]
};

export async function requestScenario(
  symbol: string,
  provider: string,
  amount: number,
  profile: FinancialProfileRequest,
  horizonDays = 30,
): Promise<InvestmentScenario> {
  return apiFetch<InvestmentScenario>("/api/scenarios/investment", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      symbol,
      provider,
      amount,
      horizon_days: horizonDays,
      profile: withProfile(profile, amount)
    })
  });
}

export async function requestDeepAnalysis(
  symbol: string,
  provider: string,
  amount: number,
  profile: FinancialProfileRequest,
  horizonDays: number,
  thesis: string,
): Promise<DeepAnalysis> {
  return apiFetch<DeepAnalysis>("/api/agents/deep-analysis", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      symbol,
      provider,
      amount,
      horizon_days: horizonDays,
      thesis,
      pro_mode: true,
      profile: withProfile(profile, amount)
    })
  });
}

export async function requestOpportunityRadar(
  provider: string,
  symbols: string[],
  amount: number,
  profile: FinancialProfileRequest,
  horizonDays: number,
): Promise<OpportunityRadar> {
  return apiFetch<OpportunityRadar>("/api/agents/opportunity-radar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      provider,
      symbols,
      amount,
      horizon_days: horizonDays,
      max_results: 3,
      profile: withProfile(profile, amount)
    })
  });
}

export async function requestMobileSession(
  symbol: string,
  provider: string,
  amount: number,
  profile: FinancialProfileRequest,
  horizonDays: number,
  thesis: string,
  watchlist: string[],
): Promise<MobileSession> {
  return apiFetch<MobileSession>("/api/mobile/session", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      symbol,
      provider,
      amount,
      horizon_days: horizonDays,
      thesis,
      watchlist,
      include_review: true,
      profile: withProfile(profile, amount)
    })
  });
}

export async function requestRunReview(runId: string): Promise<AnalysisReview> {
  return apiFetch<AnalysisReview>(`/api/agents/runs/${runId}/review`);
}

export async function openPaperPosition(
  symbol: string,
  provider: string,
  amount: number,
  thesis: string,
): Promise<PaperPosition> {
  return apiFetch<PaperPosition>("/api/portfolio/positions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ symbol, provider, amount, thesis })
  });
}

export async function listPortfolio(): Promise<PortfolioSummary> {
  return apiFetch<PortfolioSummary>("/api/portfolio/positions");
}

export async function closePaperPosition(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/portfolio/positions/${id}`, {
    method: "DELETE"
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
}

export async function requestMarketBrief(
  provider: string,
  symbols: string[],
): Promise<MarketBriefResponse> {
  return apiFetch<MarketBriefResponse>(
    `/api/markets/brief?provider=${encodeURIComponent(provider)}&symbols=${encodeURIComponent(
      symbols.join(","),
    )}`,
  );
}

export async function requestFxRate(base: Currency): Promise<FxRate> {
  return apiFetch<FxRate>(`/api/markets/fx/${base}`);
}

const demoMarket: MarketSnapshot = {
  symbol: "KSPI",
  provider: "demo_cis",
  exchange: "NASDAQ / Kazakhstan-linked ADR",
  currency: "USD",
  last_price: 121.4,
  day_change_percent: 1.2,
  volatility_30d: 0.34,
  liquidity_note: "ADR trades globally; local KZT/USD risk still matters.",
  source_note: "Demo fixture until live provider keys are connected.",
  as_of: null
};

const demoProfileSummary: ProfileSummary = {
  monthly_income: 500000,
  currency: "KZT",
  total_expenses: 350000,
  free_cash: 150000,
  safe_to_try_amount: 30000,
  status: "cautious",
  notes: ["Желаемая сумма выше безопасного лимита для эксперимента."]
};

const demoScenarios: ScenarioPoint[] = [
  { label: "Stress", outcome_percent: -50.6, projected_value: 49.4, probability_weight: 0.08 },
  { label: "Bad", outcome_percent: -30.2, projected_value: 69.8, probability_weight: 0.17 },
  { label: "Soft loss", outcome_percent: -11.5, projected_value: 88.5, probability_weight: 0.25 },
  { label: "Base gain", outcome_percent: 5.2, projected_value: 105.2, probability_weight: 0.25 },
  { label: "Good", outcome_percent: 23.9, projected_value: 123.9, probability_weight: 0.17 },
  { label: "Strong", outcome_percent: 44.3, projected_value: 144.3, probability_weight: 0.08 }
];

export const demoScenario: InvestmentScenario = {
  profile_summary: demoProfileSummary,
  market: demoMarket,
  scenarios: demoScenarios,
  agent_brief: {
    bull_case: [
      "В сильном сценарии KSPI может дать около 44.3% за горизонт.",
      "Paper tracking превращает интерес к рынку в обучающий цикл без реального приказа брокеру."
    ],
    bear_case: [
      "В стресс-сценарии позиция падает примерно до 49.4 в валюте актива.",
      "Для пользователя с бюджетом в KZT важен не только тикер, но и валютный риск."
    ],
    risk_case: [
      "ADR trades globally; local KZT/USD risk still matters.",
      "Safe-to-try сумма должна быть отдельно от аренды, долгов и базовых расходов."
    ],
    teacher_note:
      "Смысл не в том, чтобы угадать рынок. Смысл в том, чтобы увидеть диапазон исходов и понять, какая часть риска связана с активом, валютой и личным бюджетом.",
    action_note: "Открывать только учебную paper-position и уменьшить сумму до safe-to-try лимита.",
    risk_level: "elevated",
    monitoring_note: "Сегодня смотреть: изменение 1.2%, волатильность 30d 34%, источник: demo_cis.",
    disclaimer: "Educational paper-trading output only. Not investment advice."
  }
};

export const demoAnalysis: DeepAnalysis = {
  id: "demo-analysis",
  created_at: new Date(0).toISOString(),
  analysis_mode: "local_multi_agent_v1",
  horizon_days: 30,
  profile_summary: demoProfileSummary,
  market: demoMarket,
  scenarios: demoScenarios,
  evidence: [
    {
      source: "demo_cis",
      title: "KSPI normalized market snapshot",
      detail: "Price 121.4 USD, day change 1.2%, 30d volatility 34%.",
      weight: 0.8
    },
    {
      source: "personal_finance",
      title: "Household budget gate",
      detail: "Free cash 150000 KZT; safe-to-try 30000 KZT; status cautious.",
      weight: 0.9
    }
  ],
  agents: [
    {
      role: "Market Analyst",
      stance: "neutral",
      score: 4.2,
      confidence: 0.48,
      summary: "Цена растет, но источник демо и волатильность высокая.",
      evidence: ["Demo fixture", "Volatility 34%"],
      watch_items: ["price change", "volatility spike", "data freshness"]
    },
    {
      role: "Macro / FX Analyst",
      stance: "cautious",
      score: -13.5,
      confidence: 0.72,
      summary: "Актив в USD, а бытовой бюджет в KZT, поэтому итог зависит от валюты.",
      evidence: ["USD/KZT conversion needed"],
      watch_items: ["FX volatility", "NBK rate", "capital controls"]
    },
    {
      role: "Risk Manager",
      stance: "defensive",
      score: -26.2,
      confidence: 0.78,
      summary: "Paper-only режим лучше реального входа, пока сумма выше безопасного лимита.",
      evidence: ["Safe-to-try gate", "Stress scenario -50.6%"],
      watch_items: ["safe-to-try breach", "drawdown", "liquidity gap"]
    },
    {
      role: "Teacher Agent",
      stance: "explain",
      score: 0,
      confidence: 0.86,
      summary: "Главная тема урока: валютный риск и границы личного бюджета.",
      evidence: ["budget currency", "scenario distribution"],
      watch_items: ["why this thesis can be wrong", "what data changes the decision"]
    }
  ],
  debate: [
    {
      question: "Should the user test this idea now?",
      bull_response: "Да, но только как paper-эксперимент.",
      bear_response: "Нет для реальных денег: риск бюджета выше пользы от идеи.",
      risk_response: "Decision: paper_watch."
    }
  ],
  memo: {
    action: "paper_watch",
    conviction_score: 59.2,
    opportunity_score: 59.2,
    risk_score: 76.2,
    position_size_hint: "Track as paper only; cap real curiosity at 30000 KZT.",
    thesis: "KSPI: Kazakhstan fintech idea under KZT household risk.",
    invalidation_triggers: [
      "Price path approaches stress scenario.",
      "FX move erases expected result.",
      "Original thesis no longer matches evidence."
    ],
    learning_focus: [
      "currency conversion into household buying power",
      "paper thesis journal before real execution"
    ]
  },
  teacher_note:
    "Агент превращает интерес к акции в проверяемый тезис: цена, валюта, риск бюджета и правило выхода.",
  disclaimer: "Educational paper-trading analysis only. Not investment advice."
};

export const demoReview: AnalysisReview = {
  id: "demo-review",
  run_id: "demo-analysis",
  reviewed_at: new Date(0).toISOString(),
  symbol: "KSPI",
  provider: "demo_cis",
  currency: "USD",
  entry_price: 121.4,
  current_price: 121.4,
  return_percent: 0,
  days_elapsed: 0,
  horizon_days: 30,
  thesis_status: "on_track",
  verdict: "Идея пока внутри нормального учебного коридора.",
  learning_note: "Нулевой результат полезен, если пользователь учится вести тезис, а не угадывать свечу.",
  next_actions: ["keep paper tracking", "watch invalidation triggers", "compare against peer ideas"],
  source_note: "Demo fixture until live provider keys are connected."
};

export const demoRadar: OpportunityRadar = {
  analysis_mode: "local_opportunity_radar_v1",
  candidates: [
    {
      symbol: "KZTK",
      provider: "demo_cis",
      action: "small_paper_position",
      conviction_score: 64.7,
      opportunity_score: 58.1,
      risk_score: 44,
      rank_score: 45.6,
      thesis: "Local telecom infrastructure and Kazakhstan dividend story.",
      top_watch_item: "liquidity gap"
    },
    {
      symbol: "KSPI",
      provider: "demo_cis",
      action: "paper_watch",
      conviction_score: 59.2,
      opportunity_score: 59.2,
      risk_score: 76.2,
      rank_score: 38.9,
      thesis: "Kazakhstan fintech, payments, marketplace, super-app behaviour.",
      top_watch_item: "FX volatility"
    }
  ],
  note: "Ranks ideas for research priority only."
};

export const demoPortfolio: PortfolioSummary = {
  positions: [],
  total_entry_value: 0,
  total_current_value: 0,
  weighted_unrealized_percent: 0,
  note: "Paper portfolio only: tracks learning experiments without sending broker orders."
};

export const demoBrief: MarketBriefResponse = {
  provider: "demo_cis",
  symbols: ["KSPI", "AAPL", "KZTK"],
  items: [
    {
      title: "KSPI растет на 1.2%",
      body: "NASDAQ / Kazakhstan-linked ADR: цена 121.4 USD, 30d volatility 34%. Валютный риск KZT/USD остается важным.",
      priority: "medium"
    },
    {
      title: "KZTK растет на 0.6%",
      body: "KASE: цена 36120 KZT, 30d volatility 27%. Локальная ликвидность может быть тоньше глобальных акций.",
      priority: "medium"
    }
  ]
};

export const demoFx: FxRate = {
  base: "USD",
  quote: "KZT",
  rate: 540,
  change: 0,
  as_of: null,
  provider: "nbk_fallback",
  source_note: "Fallback demo FX rate."
};
