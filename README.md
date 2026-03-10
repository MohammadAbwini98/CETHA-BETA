# CETHA-BETA

CETHA-BETA is a production-oriented Python backend service for ingesting ETHUSD market data from Capital.com, computing derived 4H analytics, and storing results in PostgreSQL (`Cap_DB`, schema `CETHA_BETA`).

## 1) Architecture summary

- **API layer (`app/api_clients`)**: authenticated/retry-enabled Capital.com client.
- **Normalization layer (`app/services/normalizers.py`)**: converts raw API payloads to canonical candle records.
- **Analytics layer (`app/indicators`, `app/services/analytics.py`)**: calculates EMA20/50/200, RSI14, trend, swings, support/resistance zones, and volume behavior for 4H candles.
- **Persistence layer (`app/models`, `app/repositories`)**: SQLAlchemy models + upsert repository with deduplication.
- **Jobs layer (`app/jobs`)**: initial backfill and incremental update jobs.
- **DB migrations (`alembic`)**: reproducible schema creation and changes.

### Price methodology
Technical calculations use **mid prices** (`(bid + ask) / 2`) from Capital candle fields where bid/ask are available.

### 30M timeframe handling
`30m` is implemented in model/migration/repository mappings as an **optional extension**, disabled by default via `INCLUDE_OPTIONAL_30M=false`.

## 2) Project tree

```text
.
├── alembic/
├── app/
│   ├── api_clients/
│   ├── config/
│   ├── db/
│   ├── indicators/
│   ├── jobs/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   └── utils/
├── scripts/
├── tests/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 3) Setup instructions

1. Create virtual env and install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy and edit env:
   ```bash
   cp .env.example .env
   ```
3. Ensure PostgreSQL DB/schema exist:
   ```bash
   psql -f scripts/init_db.sql
   ```
4. Run migrations:
   ```bash
   alembic upgrade head
   ```

## 4) Operational run flow

### Initial backfill
```bash
python -m app.main backfill
```

### Incremental updater
```bash
python -m app.main update
```

Run on schedule (cron/systemd/K8s CronJob) for periodic refresh.

## 5) SQL and migration details

- DB bootstrap SQL: `scripts/init_db.sql`
- Alembic initial migration: `alembic/versions/20260310_0001_init_cetha_beta.py`
- Schema: `CETHA_BETA`
- Timeframe tables:
  - `ethusd_1m`
  - `ethusd_5m`
  - `ethusd_15m`
  - `ethusd_1h`
  - `ethusd_4h`
  - `ethusd_30m` (optional extension)

## 6) Sentiment mapping note

Capital sentiment is fetched via client sentiment endpoint and applied as the closest available snapshot for ingested candles.
It is **not guaranteed per-candle by source API** and is stored as best available approximation.

## 7) Timestamp note

Internally, timestamps are stored timezone-aware (`TIMESTAMPTZ`).
For exports/UI rendering, format with `strftime("%d-%m-%Y %H:%M:%S")`.

## 8) Tests

```bash
pytest -q
```
