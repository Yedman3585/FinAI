import { useEffect, useMemo, useState } from "react";
import {
  closePaperPosition,
  defaultProfile,
  demoAnalysis,
  demoBrief,
  demoFx,
  demoPortfolio,
  demoRadar,
  demoReview,
  demoScenario,
  listPortfolio,
  openPaperPosition,
  requestFxRate,
  requestMarketBrief,
  requestMobileSession,
  requestRunReview,
  type AnalysisReview,
  type DeepAnalysis,
  type ExpenseItem,
  type FinancialProfileRequest,
  type FxRate,
  type InvestmentScenario,
  type MarketBriefResponse,
  type OpportunityRadar,
  type PortfolioSummary,
  type ScenarioPoint
} from "./api";

type View = "money" | "idea" | "agents" | "monitor";

const providerOptions = [
  { id: "demo_cis", label: "CIS demo", symbols: ["KSPI", "AAPL", "KZTK"] },
  { id: "yahoo", label: "Yahoo", symbols: ["KSPI", "AAPL", "NVDA"] },
  { id: "moex_iss", label: "MOEX ISS", symbols: ["SBER", "GAZP", "YDEX"] }
];

const horizons = [30, 90, 180];

const views: { id: View; label: string }[] = [
  { id: "money", label: "Деньги" },
  { id: "idea", label: "Идея" },
  { id: "agents", label: "Агенты" },
  { id: "monitor", label: "Монитор" }
];

function money(value: number, currency = "KZT", compact = false) {
  return new Intl.NumberFormat("ru-KZ", {
    style: "currency",
    currency,
    maximumFractionDigits: compact ? 0 : 2
  }).format(value);
}

function percent(value: number) {
  return `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function statusLabel(value: string) {
  return value
    .replace(/_/g, " ")
    .replace("paper watch", "paper watch")
    .replace("small paper position", "small paper");
}

function App() {
  const [profile, setProfile] = useState<FinancialProfileRequest>(defaultProfile);
  const [provider, setProvider] = useState(providerOptions[0].id);
  const [symbol, setSymbol] = useState("KSPI");
  const [amount, setAmount] = useState(100);
  const [horizon, setHorizon] = useState(30);
  const [scenario, setScenario] = useState<InvestmentScenario>(demoScenario);
  const [analysis, setAnalysis] = useState<DeepAnalysis>(demoAnalysis);
  const [review, setReview] = useState<AnalysisReview>(demoReview);
  const [radar, setRadar] = useState<OpportunityRadar>(demoRadar);
  const [portfolio, setPortfolio] = useState<PortfolioSummary>(demoPortfolio);
  const [brief, setBrief] = useState<MarketBriefResponse>(demoBrief);
  const [fxRate, setFxRate] = useState<FxRate>(demoFx);
  const [view, setView] = useState<View>("idea");
  const [loading, setLoading] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [apiState, setApiState] = useState<"live" | "demo" | "error">("demo");
  const [notice, setNotice] = useState("Demo режим готов без внешних ключей.");
  const [thesis, setThesis] = useState("Хочу понять риск и поведение идеи на своих деньгах.");

  const activeProvider = providerOptions.find((item) => item.id === provider) ?? providerOptions[0];
  const totalExpenses = useMemo(
    () => profile.expenses.reduce((sum, item) => sum + item.amount, 0),
    [profile.expenses],
  );
  const freeCash = Math.max(profile.monthly_income - totalExpenses, 0);
  const amountInKzt = scenario.market.currency === "KZT" ? amount : amount * fxRate.rate;
  const safeToTry = scenario.profile_summary.safe_to_try_amount;
  const safePercent = Math.min(Math.round((amountInKzt / Math.max(safeToTry, 1)) * 100), 160);
  const riskAgent = analysis.agents.find((agent) => agent.role === "Risk Manager") ?? analysis.agents[0];
  const teacherAgent = analysis.agents.find((agent) => agent.role === "Teacher Agent");

  useEffect(() => {
    setSymbol(activeProvider.symbols[0]);
  }, [activeProvider.id]);

  useEffect(() => {
    void refreshContext(activeProvider.symbols);
  }, [provider]);

  async function refreshContext(symbols = activeProvider.symbols) {
    try {
      const [portfolioResult, briefResult, fxResult] = await Promise.all([
        listPortfolio(),
        requestMarketBrief(provider, symbols),
        requestFxRate("USD")
      ]);
      setPortfolio(portfolioResult);
      setBrief(briefResult);
      setFxRate(fxResult);
      setApiState("live");
    } catch {
      setPortfolio(demoPortfolio);
      setBrief(demoBrief);
      setFxRate(demoFx);
      setApiState("demo");
    }
  }

  function updateExpense(index: number, patch: Partial<ExpenseItem>) {
    setProfile((current) => ({
      ...current,
      expenses: current.expenses.map((item, itemIndex) =>
        itemIndex === index ? { ...item, ...patch } : item,
      )
    }));
  }

  async function runMobileAnalysis() {
    setLoading(true);
    setNotice("Считаю идею через бюджет, рынок, FX, риск и агентов...");
    try {
      const session = await requestMobileSession(
        symbol,
        provider,
        amount,
        profile,
        horizon,
        thesis,
        activeProvider.symbols,
      );
      setScenario({
        profile_summary: session.profile_summary,
        market: session.market,
        scenarios: session.scenarios,
        agent_brief: session.agent_brief
      });
      setAnalysis(session.analysis);
      setRadar(session.radar);
      setReview(session.review ?? demoReview);
      setPortfolio(session.portfolio);
      setBrief(session.market_brief);
      setFxRate(session.fx_rate ?? demoFx);
      setApiState("live");
      setNotice("Live API ответил одним mobile-session запросом.");
    } catch (error) {
      setScenario(demoScenario);
      setAnalysis(demoAnalysis);
      setRadar(demoRadar);
      setReview(demoReview);
      setApiState("demo");
      setNotice(error instanceof Error ? `Demo fallback: ${error.message}` : "Demo fallback активен.");
    } finally {
      setLoading(false);
    }
  }

  async function reviewThesis() {
    if (analysis.id === "demo-analysis") {
      setReview(demoReview);
      setNotice("Demo review: тезис пока внутри учебного коридора.");
      return;
    }
    setReviewing(true);
    try {
      const result = await requestRunReview(analysis.id);
      setReview(result);
      setApiState("live");
      setNotice(`Review готов: ${result.thesis_status}, ${percent(result.return_percent)}.`);
    } catch (error) {
      setReview(demoReview);
      setApiState("error");
      setNotice(error instanceof Error ? error.message : "Не удалось проверить тезис.");
    } finally {
      setReviewing(false);
    }
  }

  async function createPosition() {
    setLoading(true);
    setNotice("Сохраняю учебную paper-position...");
    try {
      await openPaperPosition(scenario.market.symbol, scenario.market.provider, amount, thesis);
      const portfolioResult = await listPortfolio();
      setPortfolio(portfolioResult);
      setApiState("live");
      setNotice("Paper-position сохранена без реальной сделки.");
      setView("monitor");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Не удалось открыть paper-position.");
      setApiState("error");
    } finally {
      setLoading(false);
    }
  }

  async function closePosition(id: string) {
    try {
      await closePaperPosition(id);
      setPortfolio(await listPortfolio());
      setNotice("Paper-position закрыта в локальном портфеле.");
    } catch {
      setNotice("Не удалось закрыть позицию.");
    }
  }

  return (
    <main className="app-shell">
      <section className="phone-frame">
        <header className="app-header">
          <div className="brand-row">
            <span className="brand">FInAI</span>
            <span className={`api-pill ${apiState}`}>{apiState === "live" ? "Live" : "Demo"}</span>
          </div>
          <h1>{money(safeToTry, "KZT", true)} можно безопасно тестировать</h1>
          <p>{notice}</p>
        </header>

        <section className="money-band" aria-label="Краткий статус денег">
          <Metric label="Свободно" value={money(freeCash, "KZT", true)} />
          <Metric label="Safe" value={money(safeToTry, "KZT", true)} accent />
          <Metric label="FX" value={fxRate.rate.toFixed(2)} />
        </section>

        <nav className="top-tabs" aria-label="Разделы приложения">
          {views.map((item) => (
            <button
              className={view === item.id ? "active" : ""}
              key={item.id}
              onClick={() => setView(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>

        <section className="screen-stack">
          {view === "money" && (
            <MoneyView
              freeCash={freeCash}
              profile={profile}
              setProfile={setProfile}
              totalExpenses={totalExpenses}
              updateExpense={updateExpense}
            />
          )}

          {view === "idea" && (
            <IdeaView
              activeProvider={activeProvider}
              amount={amount}
              amountInKzt={amountInKzt}
              createPosition={createPosition}
              horizon={horizon}
              loading={loading}
              provider={provider}
              providerOptions={providerOptions}
              runMobileAnalysis={runMobileAnalysis}
              safePercent={safePercent}
              safeToTry={safeToTry}
              scenario={scenario}
              setAmount={setAmount}
              setHorizon={setHorizon}
              setProvider={setProvider}
              setSymbol={setSymbol}
              setThesis={setThesis}
              symbol={symbol}
              thesis={thesis}
            />
          )}

          {view === "agents" && (
            <AgentsView
              analysis={analysis}
              radar={radar}
              review={review}
              reviewThesis={reviewThesis}
              reviewing={reviewing}
              riskAgent={riskAgent}
              teacherAgent={teacherAgent}
            />
          )}

          {view === "monitor" && (
            <MonitorView brief={brief} closePosition={closePosition} portfolio={portfolio} />
          )}
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value, accent = false }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className={accent ? "metric accent" : "metric"}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MoneyView({
  freeCash,
  profile,
  setProfile,
  totalExpenses,
  updateExpense
}: {
  freeCash: number;
  profile: FinancialProfileRequest;
  setProfile: React.Dispatch<React.SetStateAction<FinancialProfileRequest>>;
  totalExpenses: number;
  updateExpense: (index: number, patch: Partial<ExpenseItem>) => void;
}) {
  return (
    <section className="mobile-panel">
      <div className="section-head">
        <span>Бюджет</span>
        <strong>{money(freeCash, "KZT", true)}</strong>
      </div>

      <div className="input-grid">
        <label>
          Доход
          <input
            min="0"
            onChange={(event) =>
              setProfile((current) => ({
                ...current,
                monthly_income: Number(event.target.value) || 0
              }))
            }
            step="10000"
            type="number"
            value={profile.monthly_income}
          />
        </label>
        <label>
          Подушка
          <input
            min="0"
            onChange={(event) =>
              setProfile((current) => ({
                ...current,
                emergency_fund: Number(event.target.value) || 0
              }))
            }
            step="10000"
            type="number"
            value={profile.emergency_fund}
          />
        </label>
      </div>

      <div className="expense-sheet">
        {profile.expenses.map((expense, index) => (
          <label className="expense-line" key={expense.name}>
            <span>{expense.name}</span>
            <input
              aria-label={expense.name}
              min="0"
              onChange={(event) => updateExpense(index, { amount: Number(event.target.value) || 0 })}
              step="5000"
              type="number"
              value={expense.amount}
            />
          </label>
        ))}
      </div>

      <div className="ledger-row">
        <span>Расходы</span>
        <strong>{money(totalExpenses, "KZT", true)}</strong>
      </div>
    </section>
  );
}

function IdeaView({
  activeProvider,
  amount,
  amountInKzt,
  createPosition,
  horizon,
  loading,
  provider,
  providerOptions,
  runMobileAnalysis,
  safePercent,
  safeToTry,
  scenario,
  setAmount,
  setHorizon,
  setProvider,
  setSymbol,
  setThesis,
  symbol,
  thesis
}: {
  activeProvider: { id: string; label: string; symbols: string[] };
  amount: number;
  amountInKzt: number;
  createPosition: () => void;
  horizon: number;
  loading: boolean;
  provider: string;
  providerOptions: { id: string; label: string; symbols: string[] }[];
  runMobileAnalysis: () => void;
  safePercent: number;
  safeToTry: number;
  scenario: InvestmentScenario;
  setAmount: React.Dispatch<React.SetStateAction<number>>;
  setHorizon: React.Dispatch<React.SetStateAction<number>>;
  setProvider: React.Dispatch<React.SetStateAction<string>>;
  setSymbol: React.Dispatch<React.SetStateAction<string>>;
  setThesis: React.Dispatch<React.SetStateAction<string>>;
  symbol: string;
  thesis: string;
}) {
  return (
    <section className="screen-flow">
      <div className="mobile-panel market-focus">
        <div className="market-top">
          <div>
            <span>{scenario.market.exchange}</span>
            <h2>{scenario.market.symbol}</h2>
          </div>
          <div className="price-block">
            <strong>{money(scenario.market.last_price, scenario.market.currency)}</strong>
            <span className={scenario.market.day_change_percent >= 0 ? "gain" : "loss"}>
              {percent(scenario.market.day_change_percent)}
            </span>
          </div>
        </div>

        <div className="control-grid">
          <label>
            Источник
            <select value={provider} onChange={(event) => setProvider(event.target.value)}>
              {providerOptions.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Тикер
            <select value={symbol} onChange={(event) => setSymbol(event.target.value)}>
              {activeProvider.symbols.map((ticker) => (
                <option key={ticker}>{ticker}</option>
              ))}
            </select>
          </label>
          <label>
            Сумма
            <input
              min="10"
              onChange={(event) => setAmount(Number(event.target.value) || 0)}
              step="10"
              type="number"
              value={amount}
            />
          </label>
        </div>

        <div className="horizon-row" aria-label="Горизонт">
          {horizons.map((days) => (
            <button
              className={horizon === days ? "active" : ""}
              key={days}
              onClick={() => setHorizon(days)}
              type="button"
            >
              {days}d
            </button>
          ))}
        </div>

        <button className="primary-action" disabled={loading} onClick={runMobileAnalysis} type="button">
          {loading ? "Считаю..." : "Анализ"}
        </button>
      </div>

      <div className="mobile-panel">
        <div className="risk-meter">
          <div>
            <span>Сумма в KZT</span>
            <strong>{money(amountInKzt, "KZT", true)}</strong>
          </div>
          <div>
            <span>Лимит</span>
            <strong>{money(safeToTry, "KZT", true)}</strong>
          </div>
        </div>
        <div className="meter-track">
          <span style={{ width: `${safePercent}%` }} />
        </div>
      </div>

      <ScenarioList scenarios={scenario.scenarios} />

      <div className="mobile-panel action-panel">
        <span>{scenario.agent_brief.risk_level}</span>
        <strong>{scenario.agent_brief.action_note}</strong>
        <p>{scenario.agent_brief.teacher_note}</p>
      </div>

      <div className="mobile-panel">
        <label>
          Тезис
          <textarea value={thesis} onChange={(event) => setThesis(event.target.value)} />
        </label>
        <button className="secondary-action" disabled={loading} onClick={createPosition} type="button">
          Paper-position
        </button>
      </div>
    </section>
  );
}

function ScenarioList({ scenarios }: { scenarios: ScenarioPoint[] }) {
  return (
    <section className="mobile-panel">
      <div className="section-head compact">
        <span>Сценарии</span>
        <strong>{scenarios.length}</strong>
      </div>
      <div className="scenario-list">
        {scenarios.map((item) => (
          <div className="scenario-line" key={item.label}>
            <div>
              <span>{item.label}</span>
              <strong className={item.outcome_percent >= 0 ? "gain" : "loss"}>
                {percent(item.outcome_percent)}
              </strong>
            </div>
            <div className="scenario-rail">
              <span
                className={item.outcome_percent >= 0 ? "gain-bg" : "loss-bg"}
                style={{ width: `${Math.max(item.probability_weight * 100, 8)}%` }}
              />
            </div>
            <strong>{money(item.projected_value, "KZT", true)}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}

function AgentsView({
  analysis,
  radar,
  review,
  reviewThesis,
  reviewing,
  riskAgent,
  teacherAgent
}: {
  analysis: DeepAnalysis;
  radar: OpportunityRadar;
  review: AnalysisReview;
  reviewThesis: () => void;
  reviewing: boolean;
  riskAgent: DeepAnalysis["agents"][number];
  teacherAgent?: DeepAnalysis["agents"][number];
}) {
  return (
    <section className="screen-flow">
      <div className="mobile-panel memo-panel">
        <div className="section-head compact">
          <span>{analysis.market.symbol}</span>
          <strong>{statusLabel(analysis.memo.action)}</strong>
        </div>
        <div className="score-row">
          <Score label="Conviction" value={analysis.memo.conviction_score} />
          <Score label="Risk" value={analysis.memo.risk_score} danger />
        </div>
        <p>{analysis.memo.thesis}</p>
        <button className="primary-action" disabled={reviewing} onClick={reviewThesis} type="button">
          {reviewing ? "Проверяю..." : "Review thesis"}
        </button>
      </div>

      <div className="mobile-panel review-panel">
        <div className="section-head compact">
          <span>Review</span>
          <strong>{statusLabel(review.thesis_status)}</strong>
        </div>
        <div className="risk-meter">
          <div>
            <span>Return</span>
            <strong className={review.return_percent >= 0 ? "gain" : "loss"}>
              {percent(review.return_percent)}
            </strong>
          </div>
          <div>
            <span>Days</span>
            <strong>
              {review.days_elapsed}/{review.horizon_days}
            </strong>
          </div>
        </div>
        <p>{review.verdict}</p>
        <p>{review.learning_note}</p>
      </div>

      <div className="mobile-panel">
        <div className="section-head compact">
          <span>Risk desk</span>
          <strong>{riskAgent.stance}</strong>
        </div>
        <p>{riskAgent.summary}</p>
        {teacherAgent && <p>{teacherAgent.summary}</p>}
      </div>

      <div className="agent-list">
        {analysis.agents.map((agent) => (
          <article className="list-card" key={agent.role}>
            <div>
              <span>{agent.role}</span>
              <strong>{agent.stance}</strong>
            </div>
            <p>{agent.summary}</p>
          </article>
        ))}
      </div>

      <div className="mobile-panel">
        <div className="section-head compact">
          <span>Opportunity radar</span>
          <strong>{radar.candidates.length}</strong>
        </div>
        <div className="radar-list">
          {radar.candidates.map((candidate, index) => (
            <article className="radar-row" key={candidate.symbol}>
              <span>{index + 1}</span>
              <div>
                <strong>{candidate.symbol}</strong>
                <p>{statusLabel(candidate.action)} · {candidate.top_watch_item}</p>
              </div>
              <strong>{candidate.rank_score.toFixed(1)}</strong>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function Score({ label, value, danger = false }: { label: string; value: number; danger?: boolean }) {
  return (
    <div className="score">
      <span>{label}</span>
      <strong className={danger ? "loss" : "gain"}>{value.toFixed(1)}</strong>
    </div>
  );
}

function MonitorView({
  brief,
  closePosition,
  portfolio
}: {
  brief: MarketBriefResponse;
  closePosition: (id: string) => void;
  portfolio: PortfolioSummary;
}) {
  return (
    <section className="screen-flow">
      <div className="mobile-panel">
        <div className="section-head">
          <span>Paper portfolio</span>
          <strong>{percent(portfolio.weighted_unrealized_percent)}</strong>
        </div>
        <div className="position-list">
          {portfolio.positions.length === 0 ? (
            <p className="muted">Открытых paper-позиций пока нет.</p>
          ) : (
            portfolio.positions.map((position) => (
              <article className="position-row" key={position.id}>
                <div>
                  <strong>{position.symbol}</strong>
                  <span>{money(position.current_value, position.currency)}</span>
                </div>
                <div>
                  <strong className={position.unrealized_percent >= 0 ? "gain" : "loss"}>
                    {percent(position.unrealized_percent)}
                  </strong>
                  <button onClick={() => closePosition(position.id)} type="button">
                    Close
                  </button>
                </div>
              </article>
            ))
          )}
        </div>
      </div>

      <div className="brief-list">
        {brief.items.map((item) => (
          <article className={`list-card ${item.priority}`} key={item.title}>
            <div>
              <span>Market</span>
              <strong>{item.priority}</strong>
            </div>
            <h3>{item.title}</h3>
            <p>{item.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default App;
