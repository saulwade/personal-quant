import json
from pathlib import Path

from pipeline.config import Settings
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
