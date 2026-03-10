from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.models.schemas import NormalizedCandle


def _mid_price(point: dict[str, Any], side: str) -> Decimal:
    bid = Decimal(str(point.get(f"{side}Price", {}).get("bid") or point.get(f"{side}Price", {}).get("bidPrice") or 0))
    ask = Decimal(str(point.get(f"{side}Price", {}).get("ask") or point.get(f"{side}Price", {}).get("askPrice") or 0))
    if bid == 0 and ask == 0:
        return Decimal(str(point.get(side) or 0))
    return (bid + ask) / Decimal("2")


def normalize_candle(raw: dict[str, Any], instrument: str, timeframe: str, buyers: Decimal | None, sellers: Decimal | None) -> NormalizedCandle:
    open_dt = datetime.fromisoformat(raw["snapshotTimeUTC"].replace("Z", "+00:00")).astimezone(timezone.utc)
    close_dt = open_dt

    return NormalizedCandle(
        instrument=instrument,
        timeframe=timeframe,
        open_datetime=open_dt,
        close_datetime=close_dt,
        volume=Decimal(str(raw.get("lastTradedVolume"))) if raw.get("lastTradedVolume") is not None else None,
        is_closed=bool(raw.get("status", "TRADEABLE") != "PARTIAL"),
        open_price=_mid_price(raw, "open"),
        close_price=_mid_price(raw, "close"),
        high_price=_mid_price(raw, "high"),
        low_price=_mid_price(raw, "low"),
        buyers_percentage=buyers,
        sellers_percentage=sellers,
    )


def normalize_sentiment(sentiment_payload: dict[str, Any], market_id: str) -> tuple[Decimal | None, Decimal | None]:
    entries = sentiment_payload.get("clientSentiments", [])
    found = next((x for x in entries if x.get("marketId") == market_id), None)
    if not found:
        return None, None
    long_pct = Decimal(str(found.get("longPositionPercentage")))
    return long_pct, Decimal("100") - long_pct
