import pandas as pd

from pipeline.analysis.technical import build_technical_summary, score_opportunity, score_risk


def make_history(days: int = 300, start: float = 100.0, step: float = 1.0) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=days, freq="B")
    close = [start + index_value * step for index_value in range(days)]
    return pd.DataFrame({"Close": close}, index=index)


def test_technical_summary_computes_multi_horizon_metrics() -> None:
    summary = build_technical_summary(make_history())

    assert summary["observations"] == 300
    assert summary["latest_close"] == 399.0
    assert summary["return_1m_pct"] is not None
    assert summary["return_12m_pct"] is not None
    assert summary["sma_50"] is not None
    assert summary["sma_200"] is not None
    assert summary["trend"] == "uptrend"


def test_scores_return_numbers_when_enough_data_exists() -> None:
    summary = build_technical_summary(make_history())

    assert score_opportunity(summary) is not None
    assert score_risk(summary) is not None
