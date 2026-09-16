from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from app.domain.models import Currency, FxRate

NBK_RATES_URL = "https://nationalbank.kz/rss/rates_all.xml"

FALLBACK_RATES = {
    Currency.USD: 540.0,
    Currency.EUR: 635.0,
    Currency.RUB: 6.3,
}


async def get_nbk_rate(base: Currency) -> FxRate:
    if base == Currency.KZT:
        return FxRate(
            base=Currency.KZT,
            rate=1,
            change=0,
            as_of=None,
            source_note="KZT/KZT identity rate.",
        )

    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get(NBK_RATES_URL)
        response.raise_for_status()

    root = ET.fromstring(response.text)
    wanted_codes = {base.value}
    if base == Currency.RUB:
        wanted_codes.add("RUR")

    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip().upper()
        if title not in wanted_codes:
            continue

        raw_rate = float((item.findtext("description") or "0").replace(",", "."))
        quantity = float((item.findtext("quant") or "1").replace(",", "."))
        change = float((item.findtext("change") or "0").replace(",", "."))
        rate = raw_rate / quantity if quantity else raw_rate

        return FxRate(
            base=base,
            rate=round(rate, 4),
            change=round(change, 4),
            as_of=item.findtext("pubDate"),
            source_note="Official National Bank of Kazakhstan RSS market rate.",
        )

    raise ValueError(f"No NBK FX rate for {base.value}")


def fallback_rate(base: Currency, reason: str) -> FxRate:
    return FxRate(
        base=base,
        rate=FALLBACK_RATES.get(base, 1),
        change=0,
        as_of=None,
        provider="nbk_fallback",
        source_note=f"Fallback demo FX rate because live NBK request failed: {reason}",
    )
