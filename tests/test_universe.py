from pipeline.universe import get_universe, universe_by_ticker


def test_gbm_growth_universe_has_core_growth_and_mexico_assets() -> None:
    universe = get_universe("gbm-growth")
    tickers = {asset.ticker for asset in universe}

    assert "VOO" in tickers
    assert "NVDA" in tickers
    assert "NAFTRAC.MX" in tickers
    assert len(universe) >= 10


def test_universe_by_ticker_preserves_metadata() -> None:
    assets = universe_by_ticker("gbm-growth")

    assert assets["VOO"].risk_bucket == "core"
    assert assets["NVDA"].risk_bucket == "aggressive"
