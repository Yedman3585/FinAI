from app.market.providers.base import MarketDataProvider
from app.market.providers.demo_cis import DemoCisProvider
from app.market.providers.moex_iss import MoexIssProvider
from app.market.providers.yahoo import YahooFinanceProvider


providers: dict[str, MarketDataProvider] = {
    "demo_cis": DemoCisProvider(),
    "moex_iss": MoexIssProvider(),
    "yahoo": YahooFinanceProvider(),
}


def get_provider(name: str) -> MarketDataProvider:
    try:
        return providers[name]
    except KeyError as exc:
        raise ValueError(f"Unknown market provider: {name}") from exc
