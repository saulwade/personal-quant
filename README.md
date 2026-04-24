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

Initial planning and project context are in place. Implementation tasks live in:

```text
docs/superpowers/plans/2026-04-24-initial-build-openai.md
```

