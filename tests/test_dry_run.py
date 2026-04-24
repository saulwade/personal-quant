import json
from pathlib import Path

from pipeline.config import Settings
from pipeline.data.market import MarketAssetSnapshot, MarketUniverseSnapshot, write_market_snapshot
from pipeline.dry_run import run_dry_run


def test_dry_run_writes_json_and_html(tmp_path: Path) -> None:
    settings = Settings(_env_file=None, report_output_dir=tmp_path)

    analysis_path, report_path = run_dry_run(settings)

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")

    assert analysis["portfolio_health"]["overall_score"] == 76
    assert analysis_path.name == "dry-run-analysis.json"
    assert report_path.name == "dry-run-report.html"
    assert "Personal Quant Daily Report" in report


def test_dry_run_can_use_market_snapshot(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "snapshot.json"
    snapshot = MarketUniverseSnapshot(
        generated_at="2026-04-24T12:00:00+00:00",
        years_requested=5,
        assets=[
            MarketAssetSnapshot(
                ticker="VOO",
                name="VOO",
                asset_class="etf",
                market="us",
                risk_bucket="core",
                role="Broad US equity exposure",
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
                    "trend": "uptrend",
                },
                opportunity_score=78,
                risk_score=38,
            )
        ],
    )
    write_market_snapshot(snapshot, snapshot_path)
    settings = Settings(_env_file=None, report_output_dir=tmp_path / "reports")

    analysis_path, report_path = run_dry_run(settings, market_snapshot_path=snapshot_path)

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    assert analysis["ticker_analyses"][0]["ticker"] == "VOO"
    assert "VOO" in report
