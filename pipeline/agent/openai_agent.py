import json
from typing import Protocol

from openai import OpenAI

from pipeline.agent.context_builder import build_openai_market_context
from pipeline.agent.prompts import QUANT_SYSTEM_PROMPT
from pipeline.agent.schemas import InvestmentAnalysis
from pipeline.config import Settings
from pipeline.data.market import MarketUniverseSnapshot


class ResponsesClient(Protocol):
    def parse(self, **kwargs): ...


def _build_user_input(snapshot: MarketUniverseSnapshot) -> str:
    context = build_openai_market_context(snapshot)
    return json.dumps(context, ensure_ascii=False, separators=(",", ":"))


def analyze_market_snapshot_with_openai(
    snapshot: MarketUniverseSnapshot,
    settings: Settings,
    *,
    responses_client: ResponsesClient | None = None,
) -> InvestmentAnalysis:
    if not settings.openai_api_key and responses_client is None:
        raise ValueError("OPENAI_API_KEY is required for OpenAI analysis")

    client = responses_client or OpenAI(api_key=settings.openai_api_key).responses
    response = client.parse(
        model=settings.openai_model,
        instructions=QUANT_SYSTEM_PROMPT,
        input=_build_user_input(snapshot),
        text_format=InvestmentAnalysis,
        max_output_tokens=settings.openai_max_output_tokens,
        store=False,
    )

    parsed = response.output_parsed
    if not isinstance(parsed, InvestmentAnalysis):
        raise TypeError("OpenAI response did not parse as InvestmentAnalysis")
    return parsed
