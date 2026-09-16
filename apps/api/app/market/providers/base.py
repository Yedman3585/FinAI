from abc import ABC, abstractmethod

from app.domain.models import MarketSnapshot


class MarketDataProvider(ABC):
    name: str

    @abstractmethod
    async def snapshot(self, symbol: str) -> MarketSnapshot:
        """Return one normalized market snapshot for a symbol."""

