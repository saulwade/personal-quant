import pytest
from pydantic import ValidationError

from pipeline.dry_run import build_sample_analysis


def test_sample_analysis_matches_strict_schema() -> None:
    analysis = build_sample_analysis()

    assert analysis.portfolio_health.overall_score == 76
    assert analysis.ticker_analyses[0].action == "hold"
    assert analysis.portfolio_adjustments[0].urgency == "this_month"


def test_invalid_ticker_action_is_rejected() -> None:
    payload = build_sample_analysis().model_dump()
    payload["ticker_analyses"][0]["action"] = "panic_buy"

    with pytest.raises(ValidationError):
        type(build_sample_analysis()).model_validate(payload)
