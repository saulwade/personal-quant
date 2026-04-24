# Personal Quant

Personal Quant is a private investment research pipeline for building and growing a long-term portfolio from scratch.

It is not a SaaS product and it is not meant for outside users. It is a personal backend system that pulls market data, scores an investment universe, tracks a local portfolio, asks OpenAI for a structured quant-style thesis, renders an HTML report, and can email that report through Resend.

Current investor profile:

- Platform: GBM
- Country: Mexico
- Base currency: MXN
- Horizon: long term, multi-year compounding
- Risk profile: growth-oriented and aggressive, but still diversified
- Current portfolio state: can start empty and evolve over time

> Important: this tool produces research support, watchlist ideas, risk alerts, and structured analysis. It is not an automatic trading system and it does not place orders.

## What It Does Today

The current backend can already:

- Build a GBM-oriented investment universe.
- Download daily market history with `yfinance`.
- Analyze up to 5 years of data per ticker.
- Compute multi-horizon quant signals.
- Track a local portfolio file.
- Generate a mechanical report without OpenAI.
- Generate a structured OpenAI analysis using the Responses API and Pydantic Structured Outputs.
- Render a Gmail-compatible HTML report.
- Send the report to email through Resend.
- Run tests, lint, and format checks.

## Current Pipeline

```text
GBM growth universe
        |
        v
yfinance market history
        |
        v
market snapshot JSON
        |
        v
quant metrics and local portfolio context
        |
        v
OpenAI structured investment analysis
        |
        v
HTML email report
        |
        v
Resend -> inbox
```

## Architecture

```text
pipeline/
├── agent/
│   ├── context_builder.py   # compact context for OpenAI
│   ├── openai_agent.py      # Responses API structured analysis
│   ├── prompts.py           # quant analyst system prompt
│   └── schemas.py           # Pydantic response schema
├── analysis/
│   ├── market_report.py     # mechanical report from market snapshot
│   └── technical.py         # returns, momentum, volatility, trend, RSI
├── data/
│   └── market.py            # yfinance snapshot builder
├── reporting/
│   ├── email_builder.py     # HTML report renderer
│   └── sender.py            # Resend sender
├── cli.py                   # quant CLI
├── config.py                # environment settings
├── dry_run.py               # local pipeline runner
├── portfolio.py             # local portfolio storage
└── universe.py              # GBM growth universe
```

## Investment Universe

The default universe is `gbm-growth`. It is designed for a beginner investor using GBM who wants long-term growth with meaningful risk tolerance.

It includes:

- Broad ETFs: `VOO`, `VTI`, `QQQ`, `VT`
- US growth and quality: `AAPL`, `MSFT`, `NVDA`, `GOOGL`, `AMZN`, `META`
- Defensive compounders and financials: `BRK-B`, `COST`, `JPM`
- Mexico exposure: `NAFTRAC.MX`, `FEMSAUBD.MX`, `GMEXICOB.MX`, `WALMEX.MX`

This universe is a starting point. The system is meant to expand it over time as news, macro signals, portfolio needs, and investment opportunities evolve.

## Quant Signals

The market snapshot summarizes raw price history into compact signals:

- 1M, 3M, 6M, 12M, 3Y, and 5Y returns
- 12-1 momentum
- 1M, 3M, and 12M annualized volatility
- max drawdown
- SMA 50 and SMA 200
- RSI 14
- trend label: `uptrend`, `downtrend`, `mixed`, or insufficient data
- preliminary opportunity score
- preliminary risk score

The AI agent receives these summaries, not raw 5-year OHLCV tables.

## Local Files

Runtime artifacts are intentionally local and ignored by git:

```text
data/market/*.json              # market snapshots
data/portfolio/positions.json   # local portfolio state
reports/dry-run-analysis.json   # latest structured analysis
reports/dry-run-report.html     # latest email report
.env                            # local secrets
```

## Environment

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Required for OpenAI analysis:

```env
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.4
OPENAI_FALLBACK_MODEL=gpt-5.4-mini
OPENAI_MAX_OUTPUT_TOKENS=6000
```

Required for email delivery:

```env
RESEND_API_KEY=...
REPORT_EMAIL_TO=saulwade29@gmail.com
REPORT_EMAIL_FROM=onboarding@resend.dev
```

Local runtime paths:

```env
PORTFOLIO_CURRENCY=MXN
TIMEZONE=America/Monterrey
REPORT_OUTPUT_DIR=reports
MARKET_OUTPUT_DIR=data/market
PORTFOLIO_PATH=data/portfolio/positions.json
```

## Setup

Preferred setup once `uv` is installed:

```bash
uv sync --extra dev --extra data --extra reporting
```

Current local fallback:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pip install pandas numpy yfinance resend
```

## Quickstart

Initialize an empty portfolio:

```bash
quant portfolio init
quant portfolio show
```

Build a market snapshot:

```bash
quant market --universe gbm-growth --years 5
```

Generate a mechanical local report without OpenAI:

```bash
quant daily --dry-run \
  --market-snapshot data/market/gbm-growth-snapshot.json
```

Generate an OpenAI-backed report:

```bash
quant daily --dry-run \
  --market-snapshot data/market/gbm-growth-snapshot.json \
  --use-openai
```

Generate and email the report:

```bash
quant daily --dry-run \
  --market-snapshot data/market/gbm-growth-snapshot.json \
  --use-openai \
  --send-email
```

## Portfolio Commands

Initialize or show the local portfolio:

```bash
quant portfolio init
quant portfolio show
```

Add or update a position after a GBM purchase:

```bash
quant portfolio add \
  --ticker VOO \
  --shares 1 \
  --avg-buy-price 500 \
  --currency USD \
  --asset-type etf
```

Remove a position:

```bash
quant portfolio remove --ticker VOO
```

If the portfolio is empty, the OpenAI agent treats the daily report as initial portfolio construction research. Once positions exist, the portfolio context is included in the analysis.

## CLI Reference

```bash
quant market --universe gbm-growth --years 5
quant market --universe gbm-growth --tickers VOO MSFT NVDA --years 5

quant daily --dry-run
quant daily --dry-run --market-snapshot data/market/gbm-growth-snapshot.json
quant daily --dry-run --market-snapshot data/market/gbm-growth-snapshot.json --use-openai
quant daily --dry-run --market-snapshot data/market/gbm-growth-snapshot.json --use-openai --send-email

quant portfolio init
quant portfolio show
quant portfolio add --ticker VOO --shares 1 --avg-buy-price 500 --currency USD --asset-type etf
quant portfolio remove --ticker VOO
```

## Verification

```bash
pytest -v
ruff check .
black --check .
```

Full smoke test with real OpenAI and Resend:

```bash
quant market --universe gbm-growth --tickers VOO MSFT --years 5 --output data/market/smoke-snapshot.json
quant daily --dry-run --market-snapshot data/market/smoke-snapshot.json --use-openai --send-email
```

## Roadmap

Near-term:

- Persist daily analyses and snapshots in Neon PostgreSQL.
- Add macro data through FRED and market proxies like VIX, DXY, oil, gold, and treasury yields.
- Add RSS/news ingestion and FinBERT sentiment.
- Add more portfolio analytics: weights, unrealized P&L, concentration, and rebalance suggestions.
- Add APScheduler for daily 6:00 AM America/Monterrey runs.

Later:

- Add a small dashboard.
- Add richer forecasting and walk-forward validation.
- Expand the universe with sector ETFs, bonds, cash proxies, and crypto proxies available to a Mexico-based investor.

## Development Notes

- Do not commit `.env`, `data/`, or `reports/`.
- Keep API keys in `.env` only.
- The AI response is validated with Pydantic before report rendering.
- Provider failures should be isolated per source or ticker.
- Market data should be summarized before being sent to OpenAI.
- Direct order execution is intentionally out of scope.

