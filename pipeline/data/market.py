import json
from datetime import UTC, datetime
from pathlib import Path
from time import sleep
from typing import Protocol

import pandas as pd
from loguru import logger
from pydantic import BaseModel, Field

from pipeline.analysis.technical import (
    build_technical_summary,
    score_opportunity,
    score_risk,
)
from pipeline.universe import UniverseAsset


class HistoryDownloader(Protocol):
    def __call__(self, ticker: str, years: int) -> pd.DataFrame: ...


class MarketAssetSnapshot(BaseModel):
    ticker: str
    name: str | None = None
    asset_class: str | None = None
    market: str | None = None
    risk_bucket: str | None = None
    role: str | None = None
    years_requested: int
    start_date: str | None
    end_date: str | None
    observations: int
    metrics: dict[str, float | str | None]
    opportunity_score: float | None
    risk_score: float | None
    warnings: list[str] = Field(default_factory=list)


class MarketUniverseSnapshot(BaseModel):
    generated_at: str
    years_requested: int
    assets: list[MarketAssetSnapshot]
    warnings: list[str] = Field(default_factory=list)


def yfinance_history(ticker: str, years: int) -> pd.DataFrame:
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError("Install data dependencies with `pip install -e '.[data]'`.") from exc

    period = f"{years}y"
    data = yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=True)
    if not isinstance(data, pd.DataFrame):
        raise RuntimeError(f"Unexpected yfinance response for {ticker}")
    return data


def summarize_history(
    ticker: str,
    history: pd.DataFrame,
    *,
    years: int,
    asset: UniverseAsset | None = None,
) -> MarketAssetSnapshot:
    warnings: list[str] = []
    if history.empty:
        warnings.append("No market history returned")

    summary = build_technical_summary(history)
    observations = int(summary.get("observations") or 0)
    if observations and observations < min(252, years * 180):
        warnings.append("Limited market history for requested lookback")

    if history.empty:
        start_date = None
        end_date = None
    else:
        start_date = str(history.index.min().date())
        end_date = str(history.index.max().date())

    return MarketAssetSnapshot(
        ticker=ticker,
        name=asset.name if asset else None,
        asset_class=asset.asset_class if asset else None,
        market=asset.market if asset else None,
        risk_bucket=asset.risk_bucket if asset else None,
        role=asset.role if asset else None,
        years_requested=years,
        start_date=start_date,
        end_date=end_date,
        observations=observations,
        metrics=summary,
        opportunity_score=score_opportunity(summary),
        risk_score=score_risk(summary),
        warnings=warnings,
    )


def build_market_snapshot(
    tickers: list[str],
    *,
    years: int,
    universe_assets: dict[str, UniverseAsset] | None = None,
    downloader: HistoryDownloader = yfinance_history,
    request_pause_seconds: float = 0.5,
) -> MarketUniverseSnapshot:
    assets: list[MarketAssetSnapshot] = []
    warnings: list[str] = []

    for index, ticker in enumerate(tickers):
        if index > 0 and request_pause_seconds > 0:
            sleep(request_pause_seconds)

        asset = universe_assets.get(ticker) if universe_assets else None
        try:
            history = downloader(ticker, years)
            assets.append(summarize_history(ticker, history, years=years, asset=asset))
        except Exception as exc:  # noqa: BLE001 - provider failures must not stop the batch
            message = f"{ticker}: {exc}"
            logger.warning("Market data fetch failed: {}", message)
            warnings.append(message)
            assets.append(
                MarketAssetSnapshot(
                    ticker=ticker,
                    name=asset.name if asset else None,
                    asset_class=asset.asset_class if asset else None,
                    market=asset.market if asset else None,
                    risk_bucket=asset.risk_bucket if asset else None,
                    role=asset.role if asset else None,
                    years_requested=years,
                    start_date=None,
                    end_date=None,
                    observations=0,
                    metrics={"observations": 0, "latest_close": None, "trend": "error"},
                    opportunity_score=None,
                    risk_score=None,
                    warnings=[str(exc)],
                )
            )

    return MarketUniverseSnapshot(
        generated_at=datetime.now(UTC).isoformat(),
        years_requested=years,
        assets=assets,
        warnings=warnings,
    )


def write_market_snapshot(snapshot: MarketUniverseSnapshot, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot.model_dump(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def load_market_snapshot(snapshot_path: Path) -> MarketUniverseSnapshot:
    return MarketUniverseSnapshot.model_validate_json(snapshot_path.read_text(encoding="utf-8"))
