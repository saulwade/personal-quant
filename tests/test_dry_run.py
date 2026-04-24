import json
from pathlib import Path

from pipeline.config import Settings
from pipeline.data.market import write_market_snapshot
from pipeline.dry_run import run_dry_run
from tests.helpers import make_market_snapshot


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
    snapshot = make_market_snapshot()
    write_market_snapshot(snapshot, snapshot_path)
    settings = Settings(_env_file=None, report_output_dir=tmp_path / "reports")

    analysis_path, report_path = run_dry_run(settings, market_snapshot_path=snapshot_path)

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    assert analysis["ticker_analyses"][0]["ticker"] == "VOO"
    assert "VOO" in report


def test_openai_dry_run_requires_market_snapshot(tmp_path: Path) -> None:
    settings = Settings(_env_file=None, report_output_dir=tmp_path)

    try:
        run_dry_run(settings, use_openai=True)
    except ValueError as exc:
        assert "--use-openai requires --market-snapshot" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
