from decimal import Decimal

from app.indicators.ta import ema, rsi


def test_ema_returns_expected_length_and_values() -> None:
    values = [Decimal(x) for x in range(1, 31)]
    result = ema(values, 20)
    assert len(result) == len(values)
    assert result[18] is None
    assert result[19] is not None


def test_rsi_bounded() -> None:
    values = [Decimal("100") + Decimal(i) for i in range(30)]
    result = rsi(values, 14)
    computed = [x for x in result if x is not None]
    assert computed
    assert all(Decimal("0") <= x <= Decimal("100") for x in computed)
