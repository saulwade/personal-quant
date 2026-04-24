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
uv sync --extra dev
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

## Verification

```bash
pytest -v
ruff check .
black --check .
```
