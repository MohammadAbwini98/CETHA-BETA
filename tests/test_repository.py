from datetime import datetime, timezone
from decimal import Decimal

from app.models.schemas import NormalizedCandle
from app.repositories.candles import CandleRepository


class DummyDB:
    def __init__(self) -> None:
        self.executed = None
        self.committed = False

    def execute(self, stmt):
        self.executed = stmt

    def commit(self):
        self.committed = True


def test_upsert_many_executes_statement() -> None:
    db = DummyDB()
    repo = CandleRepository(db)  # type: ignore[arg-type]
    candle = NormalizedCandle(
        instrument="ETHUSD",
        timeframe="1m",
        open_datetime=datetime.now(timezone.utc),
        close_datetime=datetime.now(timezone.utc),
        volume=Decimal("1.23"),
        is_closed=True,
        open_price=Decimal("10"),
        close_price=Decimal("11"),
        high_price=Decimal("12"),
        low_price=Decimal("9"),
        buyers_percentage=Decimal("50"),
        sellers_percentage=Decimal("50"),
    )
    repo.upsert_many([candle])
    assert db.executed is not None
    assert db.committed
