from pathlib import Path

from app.domain.models import ExternalEngineStatus


PROJECT_ROOT = Path(__file__).resolve().parents[4]


def list_external_engines() -> list[ExternalEngineStatus]:
    return [
        ExternalEngineStatus(
            name="TradingAgents",
            present=(PROJECT_ROOT / "external" / "TradingAgents").exists(),
            path=str(PROJECT_ROOT / "external" / "TradingAgents"),
            license="Apache-2.0",
            role="Deep multi-agent trading research: analysts, researchers, trader, risk, portfolio manager.",
            integration_status=(
                "Copied as isolated reference engine. FInAI local_multi_agent_v1 mirrors the role model; "
                "direct execution requires separate Python 3.12 env and LLM/data API keys."
            ),
        ),
        ExternalEngineStatus(
            name="ai-hedge-fund",
            present=(PROJECT_ROOT / "external" / "ai-hedge-fund").exists(),
            path=str(PROJECT_ROOT / "external" / "ai-hedge-fund"),
            license="MIT",
            role="Mandates, backtesting, simulated broker, risk limits, and paper-fund workflows.",
            integration_status=(
                "Copied as isolated reference engine. Current FInAI paper portfolio borrows the mandate/log idea; "
                "backtest integration is the next backend milestone."
            ),
        ),
    ]
