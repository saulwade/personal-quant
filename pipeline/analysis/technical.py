import math

import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def clean_close_series(history: pd.DataFrame) -> pd.Series:
    if history.empty:
        return pd.Series(dtype="float64")

    close_column = "Close"
    if close_column not in history.columns:
        raise ValueError("Market history must include a Close column")

    close = pd.to_numeric(history[close_column], errors="coerce").dropna()
    return close.astype("float64")


def percent_return(close: pd.Series, periods: int) -> float | None:
    if len(close) <= periods:
        return None

    start = close.iloc[-periods - 1]
    end = close.iloc[-1]
    if start == 0 or pd.isna(start) or pd.isna(end):
        return None

    return round((end / start - 1) * 100, 4)


def annualized_volatility(close: pd.Series, periods: int) -> float | None:
    returns = close.pct_change().dropna()
    if len(returns) < min(periods, 2):
        return None

    window = returns.tail(periods)
    volatility = window.std() * math.sqrt(TRADING_DAYS_PER_YEAR)
    if pd.isna(volatility):
        return None
    return round(float(volatility * 100), 4)


def simple_moving_average(close: pd.Series, window: int) -> float | None:
    if len(close) < window:
        return None
    value = close.tail(window).mean()
    if pd.isna(value):
        return None
    return round(float(value), 4)


def max_drawdown(close: pd.Series) -> float | None:
    if close.empty:
        return None

    running_max = close.cummax()
    drawdown = close / running_max - 1
    value = drawdown.min()
    if pd.isna(value):
        return None
    return round(float(value * 100), 4)


def momentum_12_1(close: pd.Series) -> float | None:
    """Classic 12-1 momentum: trailing 12-month return excluding the latest month."""

    if len(close) <= 252:
        return None

    end = close.iloc[-22]
    start = close.iloc[-253]
    if start == 0 or pd.isna(start) or pd.isna(end):
        return None
    return round((end / start - 1) * 100, 4)


def trend_label(close: pd.Series) -> str:
    sma_50 = simple_moving_average(close, 50)
    sma_200 = simple_moving_average(close, 200)
    if sma_50 is None or sma_200 is None or close.empty:
        return "insufficient_data"

    latest = close.iloc[-1]
    if latest > sma_50 > sma_200:
        return "uptrend"
    if latest < sma_50 < sma_200:
        return "downtrend"
    return "mixed"


def relative_strength_index(close: pd.Series, window: int = 14) -> float | None:
    if len(close) <= window:
        return None

    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    latest_loss = loss.iloc[-1]
    latest_gain = gain.iloc[-1]
    if pd.isna(latest_gain) or pd.isna(latest_loss):
        return None
    if latest_loss == 0:
        return 100.0

    rs = latest_gain / latest_loss
    rsi = 100 - (100 / (1 + rs))
    return round(float(rsi), 4)


def build_technical_summary(history: pd.DataFrame) -> dict[str, float | str | None]:
    close = clean_close_series(history)
    if close.empty:
        return {
            "observations": 0,
            "latest_close": None,
            "trend": "no_data",
        }

    return {
        "observations": len(close),
        "latest_close": round(float(close.iloc[-1]), 4),
        "return_1m_pct": percent_return(close, 21),
        "return_3m_pct": percent_return(close, 63),
        "return_6m_pct": percent_return(close, 126),
        "return_12m_pct": percent_return(close, 252),
        "return_3y_pct": percent_return(close, 756),
        "return_5y_pct": percent_return(close, 1260),
        "momentum_12_1_pct": momentum_12_1(close),
        "volatility_1m_pct": annualized_volatility(close, 21),
        "volatility_3m_pct": annualized_volatility(close, 63),
        "volatility_12m_pct": annualized_volatility(close, 252),
        "max_drawdown_pct": max_drawdown(close),
        "sma_50": simple_moving_average(close, 50),
        "sma_200": simple_moving_average(close, 200),
        "rsi_14": relative_strength_index(close),
        "trend": trend_label(close),
    }


def score_opportunity(summary: dict[str, float | str | None]) -> float | None:
    momentum = summary.get("momentum_12_1_pct")
    trend = summary.get("trend")
    drawdown = summary.get("max_drawdown_pct")
    volatility = summary.get("volatility_12m_pct")

    if not isinstance(momentum, int | float):
        return None

    score = 50.0 + max(min(momentum, 50), -50) * 0.6
    if trend == "uptrend":
        score += 10
    elif trend == "downtrend":
        score -= 10

    if isinstance(drawdown, int | float):
        score += max(drawdown, -50) * 0.15
    if isinstance(volatility, int | float):
        score -= max(volatility - 20, 0) * 0.25

    return round(max(0, min(100, score)), 2)


def score_risk(summary: dict[str, float | str | None]) -> float | None:
    volatility = summary.get("volatility_12m_pct")
    drawdown = summary.get("max_drawdown_pct")
    if not isinstance(volatility, int | float):
        return None

    score = min(100.0, volatility * 1.4)
    if isinstance(drawdown, int | float):
        score += min(abs(drawdown), 60) * 0.35

    return round(max(0, min(100, score)), 2)
