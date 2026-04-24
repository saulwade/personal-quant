from pipeline.analysis.market_report import build_mechanical_analysis
from pipeline.data.market import MarketAssetSnapshot, MarketUniverseSnapshot


def make_asset(
    ticker: str,
    *,
    opportunity_score: float,
    risk_score: float,
    trend: str = "uptrend",
) -> MarketAssetSnapshot:
    return MarketAssetSnapshot(
        ticker=ticker,
        name=ticker,
        asset_class="etf",
        market="us",
        risk_bucket="core",
        role="Test role",
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


def test_build_mechanical_analysis_promotes_top_opportunities() -> None:
    snapshot = MarketUniverseSnapshot(
        generated_at="2026-04-24T12:00:00+00:00",
        years_requested=5,
        assets=[
            make_asset("VOO", opportunity_score=78, risk_score=38),
            make_asset("NVDA", opportunity_score=84, risk_score=82),
            make_asset("MSFT", opportunity_score=72, risk_score=45),
        ],
    )

    analysis = build_mechanical_analysis(snapshot)

    assert "Top opportunity candidates" in analysis.market_summary
    assert analysis.watchlist_updates[0].ticker == "NVDA"
    assert analysis.portfolio_adjustments
    assert any(alert.ticker if hasattr(alert, "ticker") else True for alert in analysis.risk_alerts)
    assert len(analysis.ticker_analyses) == 3
