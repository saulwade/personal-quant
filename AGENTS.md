# Personal Quant - Agent Context

## Project

Private personal investment analysis system. It runs in the background, analyzes market, macro, technical, fundamental, news, sentiment, social, forecast, and portfolio data, then emails a daily investment report.

This is not a SaaS product. There are no external users. Optimize for a reliable personal pipeline, clear logs, simple operations, and low maintenance.

## Canonical Workspace

Project root:

```text
/Users/saulwadesilva/development/Personal_Quant
```

## AI Provider

Use OpenAI API, not Anthropic Claude API.

Default model:

```text
gpt-5.4
```

Cost-sensitive fallback:

```text
gpt-5.4-mini
```

Implementation guidance:

- Prefer the OpenAI Responses API for the central investment agent.
- Use Structured Outputs with a JSON Schema for the daily analysis response.
- Keep the model name configurable through environment variables.
- Do not hardcode API keys or model strings outside config defaults.
- Validate model output with Pydantic before persisting or emailing.

## Python Stack

- Python 3.11+
- uv
- yfinance
- pandas, numpy
- pandas-ta
- statsmodels
- scikit-learn
- prophet
- scipy
- transformers, torch, FinBERT
- feedparser
- praw
- pytrends
- requests, beautifulsoup4
- fredapi
- pycoingecko or coinpaprika client
- apscheduler
- loguru
- python-dotenv
- sqlalchemy, psycopg2
- openai
- resend
- pytest
- ruff, black

## Database

Use Neon PostgreSQL with SQLAlchemy from Python.

Core tables:

- `positions`
- `transactions`
- `daily_analysis`
- `news_items`
- `watchlist`

## Environment Variables

```env
DATABASE_URL=postgresql://...neon.tech/...
FRED_API_KEY=...
NEWSAPI_KEY=...
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.4
OPENAI_FALLBACK_MODEL=gpt-5.4-mini
RESEND_API_KEY=...
REPORT_EMAIL_TO=...
REPORT_EMAIL_FROM=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=quant-personal/1.0
PORTFOLIO_CURRENCY=MXN
TIMEZONE=America/Monterrey
```

## Do Not Use

- Anthropic Claude API for the investment agent
- Alpha Vantage, Polygon.io, Quandl, Refinitiv, Bloomberg Terminal
- Telegram bot
- Docker unless explicitly requested
- Redis or Celery
- LangChain or LlamaIndex
- pandas-datareader
- TA-Lib C library
- n8n, Make.com, or no-code automations
- Paid NewsAPI tiers

## Target Architecture

```text
pipeline/
├── data/
│   ├── market.py
│   ├── macro.py
│   ├── news.py
│   ├── sentiment.py
│   └── social.py
├── analysis/
│   ├── technical.py
│   ├── fundamental.py
│   ├── statistical.py
│   ├── forecast.py
│   └── portfolio.py
├── agent/
│   ├── context_builder.py
│   ├── openai_agent.py
│   ├── schemas.py
│   └── prompts.py
├── reporting/
│   ├── email_builder.py
│   └── sender.py
├── db/
│   ├── schema.py
│   ├── portfolio.py
│   └── history.py
├── scheduler.py
├── main.py
└── config.py
```

## Development Rules

- If one data source fails, log the error and continue with partial data.
- Never hardcode portfolio tickers. Load positions and watchlist from the database.
- Respect rate limits, especially yfinance and FRED.
- Cache same-day fetched data to avoid repeated API calls.
- Compress market data before sending it to OpenAI. Do not send raw 90-day OHLCV unless explicitly needed.
- Parse and validate AI output as strict JSON.
- If model output validation fails, retry once with a concise schema repair instruction.
- Email reports must use simple inline CSS compatible with Gmail.

