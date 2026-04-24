# Personal Quant

Private personal quant-investment pipeline.

The system will collect market, macro, portfolio, news, sentiment, social, and forecast data, build a compact analysis context, use the OpenAI API to produce a structured investment thesis, persist the result, and send a daily HTML email report.

## Workspace

```text
/Users/saulwadesilva/development/Personal_Quant
```

## AI Provider

This project uses the OpenAI API.

Default model:

```text
gpt-5.4
```

Cost-sensitive fallback:

```text
gpt-5.4-mini
```

## Planned Stack

- Python 3.11+
- uv
- PostgreSQL on Neon
- SQLAlchemy
- yfinance
- FRED
- RSS feeds
- FinBERT
- OpenAI Responses API with Structured Outputs
- Resend
- APScheduler
- pytest, ruff, black

## Status

Initial planning and the first local dry-run scaffold are in place. Implementation tasks live in:

```text
docs/superpowers/plans/2026-04-24-initial-build-openai.md
```

## Local Setup

Preferred setup once `uv` is installed:

```bash
uv sync --extra dev --extra data
uv run quant daily --dry-run
```

Temporary fallback using the local virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
quant daily --dry-run
```

The dry-run does not call OpenAI, Neon, yfinance, Resend, FRED, or any other external service. It writes local artifacts to:

```text
reports/dry-run-analysis.json
reports/dry-run-report.html
```

## Market Data Snapshot

The first real data command builds a local market snapshot for an aggressive,
long-term GBM-oriented universe:

```bash
pip install pandas numpy yfinance
quant market --universe gbm-growth --years 5
```

It writes:

```text
data/market/gbm-growth-snapshot.json
```

The snapshot summarizes daily price history instead of storing raw OHLCV in the
model context. It includes:

- 1M, 3M, 6M, 12M, 3Y, and 5Y returns
- 12-1 momentum
- 1M, 3M, and 12M annualized volatility
- max drawdown
- SMA 50/200, RSI 14, and trend label
- preliminary opportunity and risk scores

The default universe includes broad ETFs, US growth stocks, defensive compounders,
and Mexican tickers available for analysis. These outputs are research signals,
not automatic buy or sell orders.

## Daily Dry-Run With Market Data

After generating a market snapshot, use it to render the daily report with real
market-derived signals:

```bash
quant daily --dry-run --market-snapshot data/market/gbm-growth-snapshot.json
```

This still does not call OpenAI, Neon, or Resend. It converts the market snapshot
into a mechanical analysis report with opportunity candidates, risk alerts,
trend/momentum notes, and preliminary watchlist entries.

## Verification

```bash
pytest -v
ruff check .
black --check .
```
