from pipeline.agent.context_builder import build_openai_market_context
from tests.helpers import make_market_snapshot


def test_openai_market_context_is_compact_and_includes_profile() -> None:
    context = build_openai_market_context(make_market_snapshot())

    assert context["investor_profile"]["platform"] == "GBM"
    assert context["investor_profile"]["risk_profile"] == "long_term_growth_aggressive"
    assert context["data_status"]["valid_assets"] == 2
    assert context["top_opportunity_screen"][0]["ticker"] == "VOO"
    assert "all_assets" in context
    assert context["portfolio"]["is_empty"] is True


def test_openai_market_context_accepts_portfolio_context() -> None:
    context = build_openai_market_context(
        make_market_snapshot(),
        portfolio={"is_empty": False, "position_count": 1, "positions": [{"ticker": "VOO"}]},
    )

    assert context["portfolio"]["is_empty"] is False
    assert context["portfolio"]["positions"][0]["ticker"] == "VOO"
