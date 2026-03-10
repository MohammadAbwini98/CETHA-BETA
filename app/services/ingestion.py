from __future__ import annotations

import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from app.api_clients.capital_client import CapitalComClient
from app.config import settings
from app.repositories.candles import CandleRepository
from app.services.analytics import derive_4h_context
from app.services.normalizers import normalize_candle, normalize_sentiment

LOGGER = logging.getLogger(__name__)

CAPITAL_RESOLUTION_MAP = {
    "1m": "MINUTE",
    "5m": "MINUTE_5",
    "15m": "MINUTE_15",
    "30m": "MINUTE_30",
    "1h": "HOUR",
    "4h": "HOUR_4",
}


class IngestionService:
    def __init__(self, db: Session, api_client: CapitalComClient):
        self.repo = CandleRepository(db)
        self.api_client = api_client

    def sync_timeframe(self, timeframe: str, max_points: int | None = None) -> int:
        market_id = settings.instrument
        sentiment_payload = self.api_client.fetch_client_sentiment([market_id])
        buyers, sellers = normalize_sentiment(sentiment_payload, market_id)
        payload = self.api_client.fetch_candles(
            epic=settings.instrument,
            resolution=CAPITAL_RESOLUTION_MAP[timeframe],
            max_points=max_points or settings.backfill_points_per_timeframe,
        )
        prices = payload.get("prices", [])
        candles = [normalize_candle(p, settings.instrument, timeframe, buyers, sellers) for p in prices]
        derived = derive_4h_context(candles) if timeframe == "4h" else None
        self.repo.upsert_many(candles, derived)
        LOGGER.info("Synced %s candles for %s", len(candles), timeframe)
        return len(candles)

    def run_backfill(self) -> dict[str, int]:
        result = {}
        for timeframe in settings.active_timeframes:
            result[timeframe] = self.sync_timeframe(timeframe)
        return result

    def run_incremental(self) -> dict[str, int]:
        result = {}
        for timeframe in settings.active_timeframes:
            last = self.repo.latest_open_time(timeframe, settings.instrument)
            points = 250 if last else 1000
            result[timeframe] = self.sync_timeframe(timeframe, max_points=points)
        return result
