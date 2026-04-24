from pipeline.data.market import MarketAssetSnapshot, MarketUniverseSnapshot


def make_market_asset(
    ticker: str = "VOO",
    *,
    opportunity_score: float = 78,
    risk_score: float = 38,
    trend: str = "uptrend",
) -> MarketAssetSnapshot:
    return MarketAssetSnapshot(
        ticker=ticker,
        name=ticker,
        asset_class="etf",
        market="us",
        risk_bucket="core",
        role="Broad market exposure",
        years_requested=5,
        start_date="2021-01-01",
        end_date="2026-01-01",
        observations=1260,
        metrics={
            "observations": 1260,
            "latest_close": 100.0,
            "return_1m_pct": 2.0,
            "return_3m_pct": 8.0,
            "return_12m_pct": 21.0,
            "momentum_12_1_pct": 18.0,
            "volatility_12m_pct": 19.0,
            "max_drawdown_pct": -12.0,
            "rsi_14": 58.0,
            "trend": trend,
        },
        opportunity_score=opportunity_score,
        risk_score=risk_score,
        warnings=[],
    )


def make_market_snapshot() -> MarketUniverseSnapshot:
    return MarketUniverseSnapshot(
        generated_at="2026-04-24T12:00:00+00:00",
        years_requested=5,
        assets=[
            make_market_asset("VOO", opportunity_score=78, risk_score=38),
            make_market_asset("MSFT", opportunity_score=73, risk_score=45),
        ],
    )
