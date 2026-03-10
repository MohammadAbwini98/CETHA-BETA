from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.config import settings
from app.db import Base

SCHEMA = settings.db_schema


class CandleMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instrument: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    open_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    close_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    volume: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    open_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    high_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    low_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    buyers_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    sellers_percentage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)


class EthUsd1m(CandleMixin, Base):
    __tablename__ = "ethusd_1m"
    __table_args__ = (
        UniqueConstraint("instrument", "open_datetime", name="uq_ethusd_1m_instrument_open"),
        {"schema": SCHEMA},
    )


class EthUsd5m(CandleMixin, Base):
    __tablename__ = "ethusd_5m"
    __table_args__ = (
        UniqueConstraint("instrument", "open_datetime", name="uq_ethusd_5m_instrument_open"),
        {"schema": SCHEMA},
    )


class EthUsd15m(CandleMixin, Base):
    __tablename__ = "ethusd_15m"
    __table_args__ = (
        UniqueConstraint("instrument", "open_datetime", name="uq_ethusd_15m_instrument_open"),
        {"schema": SCHEMA},
    )


class EthUsd1h(CandleMixin, Base):
    __tablename__ = "ethusd_1h"
    __table_args__ = (
        UniqueConstraint("instrument", "open_datetime", name="uq_ethusd_1h_instrument_open"),
        {"schema": SCHEMA},
    )


class EthUsd4h(CandleMixin, Base):
    __tablename__ = "ethusd_4h"
    trend: Mapped[str | None] = mapped_column(String(16), nullable=True)
    last_swing_high: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    last_swing_low: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    support_zones: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    resistance_zones: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    ema20: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    ema50: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    ema200: Mapped[Decimal | None] = mapped_column(Numeric(20, 8), nullable=True)
    rsi: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    volume_behavior: Mapped[str | None] = mapped_column(String(32), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)

    __table_args__ = (
        UniqueConstraint("instrument", "open_datetime", name="uq_ethusd_4h_instrument_open"),
        Index("ix_ethusd_4h_trend", "trend"),
        {"schema": SCHEMA},
    )


class EthUsd30m(CandleMixin, Base):
    __tablename__ = "ethusd_30m"
    __table_args__ = (
        UniqueConstraint("instrument", "open_datetime", name="uq_ethusd_30m_instrument_open"),
        {"schema": SCHEMA},
    )
