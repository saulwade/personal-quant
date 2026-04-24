from pipeline.analysis.market_report import build_mechanical_analysis
from pipeline.data.market import MarketUniverseSnapshot
from tests.helpers import make_market_asset


def test_build_mechanical_analysis_promotes_top_opportunities() -> None:
    snapshot = MarketUniverseSnapshot(
        generated_at="2026-04-24T12:00:00+00:00",
        years_requested=5,
        assets=[
            make_market_asset("VOO", opportunity_score=78, risk_score=38),
            make_market_asset("NVDA", opportunity_score=84, risk_score=82),
            make_market_asset("MSFT", opportunity_score=72, risk_score=45),
        ],
    )

    analysis = build_mechanical_analysis(snapshot)

    assert "Top opportunity candidates" in analysis.market_summary
    assert analysis.watchlist_updates[0].ticker == "NVDA"
    assert analysis.portfolio_adjustments
    assert any(alert.ticker if hasattr(alert, "ticker") else True for alert in analysis.risk_alerts)
    assert len(analysis.ticker_analyses) == 3
