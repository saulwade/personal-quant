# Personal Quant Initial Build With OpenAI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first reliable version of a private daily quant-investment pipeline that uses OpenAI API for structured investment analysis and sends an HTML email report.

**Architecture:** Python modules collect market, macro, portfolio, news, and sentiment inputs; analysis modules reduce those inputs into compact signals; the OpenAI agent receives a validated JSON context and returns a schema-constrained JSON thesis; persistence and email happen after validation. Keep every provider behind small modules so failures are isolated and easy to test.

**Tech Stack:** Python 3.11+, uv, yfinance, pandas, numpy, pandas-ta, SQLAlchemy, Neon PostgreSQL, OpenAI Responses API with Structured Outputs, Resend, APScheduler, pytest, ruff, black.

---

## Source Notes

OpenAI API usage is based on official OpenAI docs:

- Models page: https://developers.openai.com/api/docs/models
- GPT-5.4 model page: https://developers.openai.com/api/docs/models/gpt-5.4
- Responses API reference: https://platform.openai.com/docs/api-reference/responses
- Structured Outputs guide: https://platform.openai.com/docs/guides/structured-outputs

Default model for this project is `gpt-5.4`. Set `OPENAI_MODEL` so this can be changed without code edits.

## File Structure

- Create: `pyproject.toml` - uv project metadata, dependencies, lint and test config.
- Create: `.env.example` - all required environment variable names without secrets.
- Create: `README.md` - local setup, manual pipeline run, scheduler notes.
- Create: `pipeline/config.py` - Pydantic settings and global constants.
- Create: `pipeline/db/schema.py` - SQLAlchemy table definitions.
- Create: `pipeline/db/session.py` - database engine and session factory.
- Create: `pipeline/db/portfolio.py` - portfolio and watchlist reads.
- Create: `pipeline/db/history.py` - daily analysis persistence.
- Create: `pipeline/data/market.py` - yfinance historical prices and fundamentals.
- Create: `pipeline/data/macro.py` - FRED and market proxy macro data.
- Create: `pipeline/data/news.py` - RSS fetch and NewsAPI fallback.
- Create: `pipeline/data/sentiment.py` - FinBERT scoring interface with graceful fallback.
- Create: `pipeline/data/social.py` - Reddit and Google Trends optional signals.
- Create: `pipeline/analysis/technical.py` - technical indicators and signal summaries.
- Create: `pipeline/analysis/fundamental.py` - fundamental ratio normalization.
- Create: `pipeline/analysis/statistical.py` - volatility, Sharpe, beta, correlation, VaR.
- Create: `pipeline/analysis/forecast.py` - forecasting wrapper with optional Prophet/ARIMA.
- Create: `pipeline/analysis/portfolio.py` - P&L, weights, concentration, rebalance metrics.
- Create: `pipeline/agent/schemas.py` - Pydantic models for OpenAI output and context.
- Create: `pipeline/agent/prompts.py` - OpenAI system prompt for the quant agent.
- Create: `pipeline/agent/context_builder.py` - compact JSON context builder.
- Create: `pipeline/agent/openai_agent.py` - OpenAI Responses API call and retry logic.
- Create: `pipeline/reporting/email_builder.py` - Gmail-compatible HTML report.
- Create: `pipeline/reporting/sender.py` - Resend client wrapper.
- Create: `pipeline/main.py` - manual end-to-end run.
- Create: `pipeline/scheduler.py` - APScheduler daily job at 6:00 AM America/Monterrey.
- Create: `tests/` - focused tests for config, schemas, context builder, email builder, and pipeline failure handling.

## Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `README.md`
- Create: package directories under `pipeline/` and `tests/`

- [ ] Create the uv project files and package layout.
- [ ] Add dependencies for the initial version: `openai`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `psycopg2-binary`, `python-dotenv`, `loguru`, `pandas`, `numpy`, `yfinance`, `resend`, `apscheduler`, `pytest`, `ruff`, `black`.
- [ ] Keep heavier optional dependencies (`torch`, `transformers`, `prophet`, `pandas-ta`) in an optional dependency group if install speed becomes painful.
- [ ] Run `uv sync`.
- [ ] Run `uv run pytest` and expect zero collected tests until Task 2 adds tests.
- [ ] Commit: `chore: scaffold personal quant project`.

## Task 2: Configuration

**Files:**
- Create: `pipeline/config.py`
- Test: `tests/test_config.py`

- [ ] Write tests that verify `OPENAI_MODEL` defaults to `gpt-5.4`, `OPENAI_FALLBACK_MODEL` defaults to `gpt-5.4-mini`, timezone defaults to `America/Monterrey`, and missing required secrets raise validation errors.
- [ ] Implement Pydantic settings with environment loading from `.env`.
- [ ] Add `.env.example` entries for every required secret and runtime option.
- [ ] Run `uv run pytest tests/test_config.py -v`.
- [ ] Commit: `feat: add typed runtime settings`.

## Task 3: Database Schema

**Files:**
- Create: `pipeline/db/schema.py`
- Create: `pipeline/db/session.py`
- Test: `tests/test_schema.py`

- [ ] Define SQLAlchemy models for `positions`, `transactions`, `daily_analysis`, `news_items`, and `watchlist`.
- [ ] Use UUID primary keys, timezone-aware timestamps, JSONB for structured snapshots, and numeric columns for monetary values.
- [ ] Add tests that inspect table names and critical columns without needing a live Neon connection.
- [ ] Run `uv run pytest tests/test_schema.py -v`.
- [ ] Commit: `feat: define portfolio database schema`.

## Task 4: Portfolio Repository

**Files:**
- Create: `pipeline/db/portfolio.py`
- Test: `tests/test_portfolio_repo.py`

- [ ] Implement functions to list active positions, list watchlist tickers, and upsert latest position pricing.
- [ ] Add tests using SQLite or SQLAlchemy in-memory metadata where possible.
- [ ] Keep repository functions small and explicit.
- [ ] Run `uv run pytest tests/test_portfolio_repo.py -v`.
- [ ] Commit: `feat: add portfolio repository helpers`.

## Task 5: Market Data Provider

**Files:**
- Create: `pipeline/data/market.py`
- Test: `tests/test_market.py`

- [ ] Implement yfinance fetch for compact 90-day price summaries per ticker.
- [ ] Include latest price, 1-day return, 5-day return, 30-day return, 90-day return, average volume, volatility, 52-week high/low when available, and selected fundamentals.
- [ ] Add `time.sleep(0.5)` between ticker fetches.
- [ ] Catch provider errors per ticker and return structured warnings instead of failing the entire batch.
- [ ] Mock yfinance in tests.
- [ ] Run `uv run pytest tests/test_market.py -v`.
- [ ] Commit: `feat: add resilient market data fetcher`.

## Task 6: Technical And Portfolio Analysis

**Files:**
- Create: `pipeline/analysis/technical.py`
- Create: `pipeline/analysis/portfolio.py`
- Test: `tests/test_technical.py`
- Test: `tests/test_portfolio_analysis.py`

- [ ] Implement RSI, moving average, volatility, Bollinger-style band, and trend summaries using pandas operations first.
- [ ] Add optional pandas-ta integration only if available.
- [ ] Implement portfolio total value, unrealized P&L, weights, and concentration warnings.
- [ ] Add deterministic dataframe tests.
- [ ] Run `uv run pytest tests/test_technical.py tests/test_portfolio_analysis.py -v`.
- [ ] Commit: `feat: add technical and portfolio analytics`.

## Task 7: OpenAI Agent Schema

**Files:**
- Create: `pipeline/agent/schemas.py`
- Test: `tests/test_agent_schemas.py`

- [ ] Define Pydantic models for the full required JSON response: market summary, portfolio health, ticker analyses, watchlist updates, risk alerts, portfolio adjustments, macro outlook, and opportunities.
- [ ] Restrict action fields with enums: `hold`, `buy_more`, `reduce`, `sell`, `watch`, `buy`, `rebalance`.
- [ ] Add tests that parse a complete sample response and reject an invalid action.
- [ ] Run `uv run pytest tests/test_agent_schemas.py -v`.
- [ ] Commit: `feat: define structured OpenAI agent output`.

## Task 8: Context Builder

**Files:**
- Create: `pipeline/agent/context_builder.py`
- Test: `tests/test_context_builder.py`

- [ ] Build a compact context object from portfolio, market summaries, technical signals, fundamentals, macro context, news sentiment, social signals, forecasts, and watchlist.
- [ ] Enforce a compact representation that avoids raw OHLCV arrays.
- [ ] Add tests confirming the output includes required top-level sections and excludes raw candle arrays.
- [ ] Run `uv run pytest tests/test_context_builder.py -v`.
- [ ] Commit: `feat: build compact model context`.

## Task 9: OpenAI Agent Client

**Files:**
- Create: `pipeline/agent/prompts.py`
- Create: `pipeline/agent/openai_agent.py`
- Test: `tests/test_openai_agent.py`

- [ ] Write the quant investor system prompt adapted for OpenAI, requiring strict JSON and evidence-based recommendations.
- [ ] Implement a Responses API client that sends the compact context and requests Structured Outputs using the Pydantic schema.
- [ ] Use `OPENAI_MODEL` as default and retry once with a schema-repair instruction if parsing fails.
- [ ] Mock the OpenAI client in tests. Do not call the live API from tests.
- [ ] Run `uv run pytest tests/test_openai_agent.py -v`.
- [ ] Commit: `feat: add OpenAI quant agent`.

## Task 10: Report Email

**Files:**
- Create: `pipeline/reporting/email_builder.py`
- Create: `pipeline/reporting/sender.py`
- Test: `tests/test_email_builder.py`

- [ ] Build inline-CSS HTML sections in this order: header, risk alerts, macro context, recommended actions, ticker analyses, watchlist, portfolio health.
- [ ] Implement Resend send wrapper with clear logging and no secret leakage.
- [ ] Add snapshot-style tests for key HTML sections.
- [ ] Run `uv run pytest tests/test_email_builder.py -v`.
- [ ] Commit: `feat: add daily email report builder`.

## Task 11: End-To-End Manual Pipeline

**Files:**
- Create: `pipeline/main.py`
- Modify: all provider modules as needed
- Test: `tests/test_pipeline_failure_handling.py`

- [ ] Wire the manual run flow: read portfolio, fetch data, analyze, build context, call OpenAI, persist, build email, send.
- [ ] Add failure handling so a provider failure logs a warning and the pipeline continues with available data.
- [ ] Add tests where one mocked provider fails and the pipeline still reaches context building.
- [ ] Run `uv run pytest tests/test_pipeline_failure_handling.py -v`.
- [ ] Commit: `feat: wire manual daily pipeline`.

## Task 12: Scheduler

**Files:**
- Create: `pipeline/scheduler.py`
- Test: `tests/test_scheduler.py`

- [ ] Schedule the daily job at 6:00 AM in `America/Monterrey`.
- [ ] Add logs for start, finish, duration, and failure.
- [ ] Add tests for timezone and trigger configuration.
- [ ] Run `uv run pytest tests/test_scheduler.py -v`.
- [ ] Commit: `feat: schedule daily quant report`.

## Task 13: Full Verification

**Files:**
- Modify only files needed for fixes discovered during verification.

- [ ] Run `uv run ruff check .`.
- [ ] Run `uv run black --check .`.
- [ ] Run `uv run pytest -v`.
- [ ] Run a dry-run pipeline mode that skips live OpenAI and Resend calls.
- [ ] Document the manual command in `README.md`.
- [ ] Commit: `test: verify initial personal quant pipeline`.

## Self-Review

- Spec coverage: This plan covers setup, database, data fetch, analysis, OpenAI agent, email, scheduler, and failure handling. Dashboard work is intentionally excluded until the backend pipeline works.
- Placeholder scan: No task depends on an undefined future provider. Optional social, sentiment, and forecast depth can be expanded after the first working pipeline.
- Type consistency: The OpenAI output schema lives in `pipeline/agent/schemas.py`; the context builder and OpenAI client both depend on it.

