from typing import Literal

from pydantic import BaseModel, Field

TickerAction = Literal["hold", "buy_more", "reduce", "sell", "watch"]
AdjustmentAction = Literal["buy", "sell", "rebalance"]
Urgency = Literal["immediate", "this_week", "this_month"]
Confidence = Literal["high", "medium", "low"]
RiskSeverity = Literal["high", "medium", "low"]
RiskType = Literal["concentration", "drawdown", "macro", "correlation", "liquidity"]


class PortfolioHealth(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    commentary: str
    diversification_notes: str


class TickerAnalysis(BaseModel):
    ticker: str
    technical_view: str
    fundamental_view: str
    sentiment_view: str
    forecast_view: str
    integrated_thesis: str
    action: TickerAction
    action_reasoning: str
    confidence: Confidence
    risk_factors: list[str]


class WatchlistUpdate(BaseModel):
    ticker: str
    thesis: str
    entry_trigger: str


class RiskAlert(BaseModel):
    severity: RiskSeverity
    type: RiskType
    description: str
    suggested_action: str


class PortfolioAdjustment(BaseModel):
    action: AdjustmentAction
    ticker: str
    rationale: str
    urgency: Urgency


class Opportunity(BaseModel):
    ticker: str
    why_interesting: str


class InvestmentAnalysis(BaseModel):
    market_summary: str
    portfolio_health: PortfolioHealth
    ticker_analyses: list[TickerAnalysis]
    watchlist_updates: list[WatchlistUpdate]
    risk_alerts: list[RiskAlert]
    portfolio_adjustments: list[PortfolioAdjustment]
    macro_outlook: str
    opportunities_spotted: list[Opportunity]


class DryRunResult(BaseModel):
    analysis: InvestmentAnalysis
    report_html: str
    analysis_path: str
    report_path: str
