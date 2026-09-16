from __future__ import annotations

from datetime import date, timedelta
from statistics import stdev
from typing import Any, Optional

import httpx

from app.domain.models import Currency, MarketSnapshot
from app.market.providers.base import MarketDataProvider


def _table_rows(payload: dict[str, Any], table: str) -> list[dict[str, Any]]:
    block = payload.get(table) or {}
    columns = block.get("columns") or []
    return [dict(zip(columns, row)) for row in block.get("data") or []]


class MoexIssProvider(MarketDataProvider):
    name = "moex_iss"
    base_url = "https://iss.moex.com/iss"

    async def snapshot(self, symbol: str) -> MarketSnapshot:
        security = symbol.upper().replace(".ME", "")
        async with httpx.AsyncClient(timeout=10) as client:
            security_response = await client.get(
                f"{self.base_url}/engines/stock/markets/shares/securities/{security}.json",
                params={"iss.meta": "off", "iss.only": "securities,marketdata"},
            )
            security_response.raise_for_status()
            history_response = await client.get(
                f"{self.base_url}/history/engines/stock/markets/shares/securities/{security}.json",
                params={
                    "iss.meta": "off",
                    "from": (date.today() - timedelta(days=65)).isoformat(),
                },
            )
            history_response.raise_for_status()

        payload = security_response.json()
        market_rows = _table_rows(payload, "marketdata")
        security_rows = _table_rows(payload, "securities")
        row = self._best_market_row(market_rows)
        if row is None:
            raise ValueError(f"No live MOEX market data for {security}")

        last = self._first_number(row, ["LAST", "LCURRENTPRICE", "MARKETPRICE", "BID", "OFFER"])
        if last is None:
            raise ValueError(f"No MOEX last price for {security}")

        change = self._first_number(row, ["LASTCHANGEPRCNT", "LCLOSEPRICE_CHANGE", "CHANGE"])
        board = row.get("BOARDID") or (security_rows[0].get("BOARDID") if security_rows else "MOEX")
        short_name = security_rows[0].get("SHORTNAME") if security_rows else security
        currency_code = (security_rows[0].get("FACEUNIT") if security_rows else None) or "RUB"

        volatility = self._history_volatility(history_response.json())

        return MarketSnapshot(
            symbol=security,
            provider=self.name,
            exchange=f"MOEX {board} / {short_name}",
            currency=Currency.RUB if currency_code == "SUR" else Currency.RUB,
            last_price=round(last, 4),
            day_change_percent=round(change or 0, 2),
            volatility_30d=round(volatility, 3),
            liquidity_note=self._liquidity_note(row),
            source_note="Live public MOEX ISS market data; delayed/availability depends on MOEX.",
            as_of=row.get("SYSTIME") or row.get("UPDATETIME"),
        )

    @staticmethod
    def _first_number(row: dict[str, Any], columns: list[str]) -> Optional[float]:
        for column in columns:
            value = row.get(column)
            if value is None or value == "":
                continue
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
        return None

    @staticmethod
    def _best_market_row(rows: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
        with_prices = [
            row for row in rows if MoexIssProvider._first_number(row, ["LAST", "LCURRENTPRICE", "BID"])
        ]
        if not with_prices:
            return rows[0] if rows else None
        return max(with_prices, key=lambda row: float(row.get("VALTODAY") or 0))

    @staticmethod
    def _history_volatility(payload: dict[str, Any]) -> float:
        closes: list[float] = []
        for row in _table_rows(payload, "history"):
            value = row.get("CLOSE") or row.get("LEGALCLOSEPRICE")
            if value is None:
                continue
            closes.append(float(value))

        returns = [
            (current - previous) / previous
            for previous, current in zip(closes, closes[1:])
            if previous
        ]
        if len(returns) < 2:
            return 0.25
        return stdev(returns) * (252**0.5)

    @staticmethod
    def _liquidity_note(row: dict[str, Any]) -> str:
        turnover = row.get("VALTODAY") or 0
        trades = row.get("NUMTRADES") or 0
        return (
            f"MOEX turnover today: {turnover}; trades: {trades}. "
            "Check board liquidity before any real execution."
        )
