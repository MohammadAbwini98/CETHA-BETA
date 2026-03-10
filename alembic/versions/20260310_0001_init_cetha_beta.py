"""init cetha beta schema tables

Revision ID: 20260310_0001
Revises: 
Create Date: 2026-03-10 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260310_0001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "CETHA_BETA"


def _base_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("instrument", sa.String(length=32), nullable=False),
        sa.Column("open_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("close_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("volume", sa.Numeric(20, 8), nullable=True),
        sa.Column("is_closed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open_price", sa.Numeric(20, 8), nullable=False),
        sa.Column("close_price", sa.Numeric(20, 8), nullable=False),
        sa.Column("high_price", sa.Numeric(20, 8), nullable=False),
        sa.Column("low_price", sa.Numeric(20, 8), nullable=False),
        sa.Column("buyers_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("sellers_percentage", sa.Numeric(5, 2), nullable=True),
    ]


def _create_candle_table(name: str) -> None:
    op.create_table(
        name,
        *_base_columns(),
        sa.UniqueConstraint("instrument", "open_datetime", name=f"uq_{name}_instrument_open"),
        schema=SCHEMA,
    )
    op.create_index(f"ix_{name}_instrument", name, ["instrument"], unique=False, schema=SCHEMA)
    op.create_index(f"ix_{name}_open_datetime", name, ["open_datetime"], unique=False, schema=SCHEMA)
    op.create_index(f"ix_{name}_close_datetime", name, ["close_datetime"], unique=False, schema=SCHEMA)


def upgrade() -> None:
    op.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"'))
    for table in ["ethusd_1m", "ethusd_5m", "ethusd_15m", "ethusd_1h", "ethusd_30m"]:
        _create_candle_table(table)

    op.create_table(
        "ethusd_4h",
        *_base_columns(),
        sa.Column("trend", sa.String(length=16), nullable=True),
        sa.Column("last_swing_high", sa.Numeric(20, 8), nullable=True),
        sa.Column("last_swing_low", sa.Numeric(20, 8), nullable=True),
        sa.Column("support_zones", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("resistance_zones", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ema20", sa.Numeric(20, 8), nullable=True),
        sa.Column("ema50", sa.Numeric(20, 8), nullable=True),
        sa.Column("ema200", sa.Numeric(20, 8), nullable=True),
        sa.Column("rsi", sa.Numeric(10, 4), nullable=True),
        sa.Column("volume_behavior", sa.String(length=32), nullable=True),
        sa.Column("notes", sa.String(length=512), nullable=True),
        sa.UniqueConstraint("instrument", "open_datetime", name="uq_ethusd_4h_instrument_open"),
        schema=SCHEMA,
    )
    op.create_index("ix_ethusd_4h_instrument", "ethusd_4h", ["instrument"], unique=False, schema=SCHEMA)
    op.create_index("ix_ethusd_4h_open_datetime", "ethusd_4h", ["open_datetime"], unique=False, schema=SCHEMA)
    op.create_index("ix_ethusd_4h_close_datetime", "ethusd_4h", ["close_datetime"], unique=False, schema=SCHEMA)
    op.create_index("ix_ethusd_4h_trend", "ethusd_4h", ["trend"], unique=False, schema=SCHEMA)


def downgrade() -> None:
    for table in ["ethusd_4h", "ethusd_30m", "ethusd_1h", "ethusd_15m", "ethusd_5m", "ethusd_1m"]:
        op.drop_table(table, schema=SCHEMA)
