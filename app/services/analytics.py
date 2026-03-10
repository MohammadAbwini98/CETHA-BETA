from __future__ import annotations

from decimal import Decimal

from app.indicators.ta import detect_swings, ema, rsi
from app.models.schemas import Derived4H, NormalizedCandle


def _volume_behavior(volumes: list[Decimal | None]) -> str:
    cleaned = [v for v in volumes if v is not None]
    if len(cleaned) < 5:
        return "insufficient_data"
    recent = sum(cleaned[-3:]) / Decimal("3")
    prev = sum(cleaned[-5:-2]) / Decimal("3")
    if recent > prev * Decimal("1.2"):
        return "expansion"
    if recent < prev * Decimal("0.8"):
        return "contraction"
    return "stable"


def _zones_from_swings(last_swing_high: Decimal | None, last_swing_low: Decimal | None) -> tuple[list[dict], list[dict]]:
    support = []
    resistance = []
    if last_swing_low is not None:
        support.append({"lower": float(last_swing_low * Decimal("0.995")), "upper": float(last_swing_low * Decimal("1.005"))})
    if last_swing_high is not None:
        resistance.append({"lower": float(last_swing_high * Decimal("0.995")), "upper": float(last_swing_high * Decimal("1.005"))})
    return support, resistance


def derive_4h_context(candles: list[NormalizedCandle]) -> list[Derived4H]:
    closes = [c.close_price for c in candles]
    highs = [c.high_price for c in candles]
    lows = [c.low_price for c in candles]
    volumes = [c.volume for c in candles]

    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200)
    rsi14 = rsi(closes, 14)
    swing_high, swing_low = detect_swings(highs, lows)
    support, resistance = _zones_from_swings(swing_high, swing_low)

    result: list[Derived4H] = []
    for i, candle in enumerate(candles):
        trend = "ranging"
        if ema20[i] and ema50[i] and candle.close_price > ema20[i] > ema50[i]:
            trend = "bullish"
        elif ema20[i] and ema50[i] and candle.close_price < ema20[i] < ema50[i]:
            trend = "bearish"
        result.append(
            Derived4H(
                trend=trend,
                last_swing_high=swing_high,
                last_swing_low=swing_low,
                support_zones=support,
                resistance_zones=resistance,
                ema20=ema20[i],
                ema50=ema50[i],
                ema200=ema200[i],
                rsi=rsi14[i],
                volume_behavior=_volume_behavior(volumes[: i + 1]),
            )
        )
    return result
