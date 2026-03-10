from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import EthUsd15m, EthUsd1h, EthUsd1m, EthUsd30m, EthUsd4h, EthUsd5m
from app.models.schemas import Derived4H, NormalizedCandle

MODEL_BY_TIMEFRAME: dict[str, Any] = {
    "1m": EthUsd1m,
    "5m": EthUsd5m,
    "15m": EthUsd15m,
    "1h": EthUsd1h,
    "4h": EthUsd4h,
    "30m": EthUsd30m,
}


class CandleRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_many(self, candles: list[NormalizedCandle], derived: list[Derived4H] | None = None) -> None:
        if not candles:
            return
        model = MODEL_BY_TIMEFRAME[candles[0].timeframe]
        rows = []
        now = datetime.now(timezone.utc)
        for idx, c in enumerate(candles):
            row = {
                "instrument": c.instrument,
                "open_datetime": c.open_datetime,
                "close_datetime": c.close_datetime,
                "volume": c.volume,
                "is_closed": c.is_closed,
                "created_at": now,
                "updated_at": now,
                "open_price": c.open_price,
                "close_price": c.close_price,
                "high_price": c.high_price,
                "low_price": c.low_price,
                "buyers_percentage": c.buyers_percentage,
                "sellers_percentage": c.sellers_percentage,
            }
            if c.timeframe == "4h" and derived:
                d = derived[idx]
                row.update(
                    trend=d.trend,
                    last_swing_high=d.last_swing_high,
                    last_swing_low=d.last_swing_low,
                    support_zones=d.support_zones,
                    resistance_zones=d.resistance_zones,
                    ema20=d.ema20,
                    ema50=d.ema50,
                    ema200=d.ema200,
                    rsi=d.rsi,
                    volume_behavior=d.volume_behavior,
                    notes=d.notes,
                )
            rows.append(row)
        stmt = insert(model).values(rows)
        excluded = stmt.excluded
        update_cols = {col: getattr(excluded, col) for col in rows[0].keys() if col not in {"created_at"}}
        stmt = stmt.on_conflict_do_update(
            index_elements=["instrument", "open_datetime"],
            set_=update_cols,
        )
        self.db.execute(stmt)
        self.db.commit()

    def latest_open_time(self, timeframe: str, instrument: str) -> datetime | None:
        model = MODEL_BY_TIMEFRAME[timeframe]
        q = select(model.open_datetime).where(model.instrument == instrument).order_by(model.open_datetime.desc()).limit(1)
        return self.db.execute(q).scalar_one_or_none()
