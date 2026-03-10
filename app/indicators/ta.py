from __future__ import annotations

from decimal import Decimal


def ema(series: list[Decimal], period: int) -> list[Decimal | None]:
    if not series:
        return []
    k = Decimal("2") / Decimal(period + 1)
    out: list[Decimal | None] = [None] * len(series)
    if len(series) < period:
        return out
    seed = sum(series[:period]) / Decimal(period)
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(series)):
        prev = (series[i] - prev) * k + prev
        out[i] = prev
    return out


def rsi(series: list[Decimal], period: int = 14) -> list[Decimal | None]:
    out: list[Decimal | None] = [None] * len(series)
    if len(series) <= period:
        return out
    gains = []
    losses = []
    for i in range(1, period + 1):
        diff = series[i] - series[i - 1]
        gains.append(max(diff, Decimal("0")))
        losses.append(abs(min(diff, Decimal("0"))))
    avg_gain = sum(gains) / Decimal(period)
    avg_loss = sum(losses) / Decimal(period)
    rs = avg_gain / avg_loss if avg_loss != 0 else Decimal("999")
    out[period] = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
    for i in range(period + 1, len(series)):
        diff = series[i] - series[i - 1]
        gain = max(diff, Decimal("0"))
        loss = abs(min(diff, Decimal("0")))
        avg_gain = ((avg_gain * (period - 1)) + gain) / Decimal(period)
        avg_loss = ((avg_loss * (period - 1)) + loss) / Decimal(period)
        rs = avg_gain / avg_loss if avg_loss != 0 else Decimal("999")
        out[i] = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
    return out


def detect_swings(highs: list[Decimal], lows: list[Decimal], window: int = 2) -> tuple[Decimal | None, Decimal | None]:
    last_high = None
    last_low = None
    for i in range(window, len(highs) - window):
        if highs[i] == max(highs[i - window : i + window + 1]):
            last_high = highs[i]
        if lows[i] == min(lows[i - window : i + window + 1]):
            last_low = lows[i]
    return last_high, last_low
