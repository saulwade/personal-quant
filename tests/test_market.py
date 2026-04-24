import pandas as pd

from pipeline.data.market import build_market_snapshot
from pipeline.universe import universe_by_ticker


def make_history(days: int = 320) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=days, freq="B")
    return pd.DataFrame({"Close": [100 + value for value in range(days)]}, index=index)


def test_market_snapshot_summarizes_assets_with_universe_metadata() -> None:
    def downloader(ticker: str, years: int) -> pd.DataFrame:
        assert ticker == "VOO"
        assert years == 5
        return make_history()

    snapshot = build_market_snapshot(
        ["VOO"],
        years=5,
        universe_assets=universe_by_ticker("gbm-growth"),
        downloader=downloader,
        request_pause_seconds=0,
    )

    asset = snapshot.assets[0]
    assert asset.ticker == "VOO"
    assert asset.risk_bucket == "core"
    assert asset.metrics["trend"] == "uptrend"
    assert asset.opportunity_score is not None


def test_market_snapshot_keeps_going_when_one_ticker_fails() -> None:
    def downloader(ticker: str, years: int) -> pd.DataFrame:
        if ticker == "BROKEN":
            raise RuntimeError("provider timeout")
        return make_history()

    snapshot = build_market_snapshot(
        ["VOO", "BROKEN"],
        years=5,
        universe_assets=universe_by_ticker("gbm-growth"),
        downloader=downloader,
        request_pause_seconds=0,
    )

    assert len(snapshot.assets) == 2
    assert snapshot.assets[0].observations == 320
    assert snapshot.assets[1].observations == 0
    assert "provider timeout" in snapshot.assets[1].warnings[0]
    assert snapshot.warnings
