from pipeline.agent.openai_agent import analyze_market_snapshot_with_openai
from pipeline.config import Settings
from pipeline.dry_run import build_sample_analysis
from tests.helpers import make_market_snapshot


class FakeParsedResponse:
    def __init__(self, output_parsed):
        self.output_parsed = output_parsed


class FakeResponsesClient:
    def __init__(self):
        self.kwargs = None

    def parse(self, **kwargs):
        self.kwargs = kwargs
        return FakeParsedResponse(build_sample_analysis())


def test_openai_agent_uses_structured_outputs_schema() -> None:
    client = FakeResponsesClient()
    settings = Settings(_env_file=None, openai_api_key="test-key")

    analysis = analyze_market_snapshot_with_openai(
        make_market_snapshot(),
        settings,
        responses_client=client,
    )

    assert analysis.market_summary
    assert client.kwargs["model"] == "gpt-5.4"
    assert client.kwargs["text_format"].__name__ == "InvestmentAnalysis"
    assert client.kwargs["store"] is False
