from pipeline.dry_run import build_sample_analysis
from pipeline.reporting.email_builder import build_daily_report_html


def test_email_builder_renders_core_sections() -> None:
    html = build_daily_report_html(build_sample_analysis(), portfolio_value="100,000 MXN")

    assert "Personal Quant Daily Report" in html
    assert "Risk Alerts" in html
    assert "Recommended Actions" in html
    assert "Ticker Analysis" in html
    assert "Portfolio Health" in html
    assert "100,000 MXN" in html
