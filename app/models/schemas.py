from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class NormalizedCandle:
    instrument: str
    timeframe: str
    open_datetime: datetime
    close_datetime: datetime
    volume: Decimal | None
    is_closed: bool
    open_price: Decimal
    close_price: Decimal
    high_price: Decimal
    low_price: Decimal
    buyers_percentage: Decimal | None
    sellers_percentage: Decimal | None


@dataclass(slots=True)
class Derived4H:
    trend: str
    last_swing_high: Decimal | None
    last_swing_low: Decimal | None
    support_zones: list[dict]
    resistance_zones: list[dict]
    ema20: Decimal | None
    ema50: Decimal | None
    ema200: Decimal | None
    rsi: Decimal | None
    volume_behavior: str
    notes: str | None = None
