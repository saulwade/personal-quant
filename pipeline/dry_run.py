import json
from pathlib import Path

from pipeline.agent.schemas import (
    InvestmentAnalysis,
    Opportunity,
    PortfolioAdjustment,
    PortfolioHealth,
    RiskAlert,
    TickerAnalysis,
    WatchlistUpdate,
)
from pipeline.config import Settings
from pipeline.reporting.email_builder import build_daily_report_html


def build_sample_analysis() -> InvestmentAnalysis:
    """Return a deterministic sample analysis for local pipeline verification."""

    return InvestmentAnalysis(
        market_summary=(
            "Dry-run macro context: broad equity risk is neutral, volatility is controlled, "
            "and USD/MXN exposure should be monitored before adding more US assets."
        ),
        portfolio_health=PortfolioHealth(
            overall_score=76,
            commentary=(
                "The sample portfolio is healthy but still concentrated in US mega-cap tech."
            ),
            diversification_notes=(
                "Add non-tech exposure before increasing single-name concentration."
            ),
        ),
        ticker_analyses=[
            TickerAnalysis(
                ticker="AAPL",
                technical_view="Price is above the 50-day average with RSI in a neutral zone.",
                fundamental_view=(
                    "Quality remains high, but valuation leaves limited margin of safety."
                ),
                sentiment_view="News tone is neutral-to-positive with no urgent negative catalyst.",
                forecast_view="Dry-run forecast suggests modest upside with normal volatility.",
                integrated_thesis="Hold the position while waiting for a better entry to add.",
                action="hold",
                action_reasoning=(
                    "The signal set is constructive but not strong enough for new buying."
                ),
                confidence="medium",
                risk_factors=["Valuation compression", "Single-name concentration"],
            ),
            TickerAnalysis(
                ticker="MSFT",
                technical_view="Trend is positive and drawdown is contained.",
                fundamental_view="Margins and recurring revenue profile remain attractive.",
                sentiment_view="AI and cloud sentiment remains supportive.",
                forecast_view="Dry-run forecast favors steady compounding over sharp upside.",
                integrated_thesis="A measured add can be justified if portfolio weight allows it.",
                action="buy_more",
                action_reasoning="Higher-quality signal mix than other sample holdings.",
                confidence="medium",
                risk_factors=["AI capex expectations", "Market multiple compression"],
            ),
        ],
        watchlist_updates=[
            WatchlistUpdate(
                ticker="NVDA",
                thesis="Strong secular AI demand, but entry discipline matters after large moves.",
                entry_trigger="Consider entry on a pullback toward the 50-day moving average.",
            )
        ],
        risk_alerts=[
            RiskAlert(
                severity="medium",
                type="concentration",
                description="Sample portfolio is overweight US large-cap technology.",
                suggested_action=(
                    "Avoid adding more correlated tech exposure until weights are updated."
                ),
            )
        ],
        portfolio_adjustments=[
            PortfolioAdjustment(
                action="buy",
                ticker="MSFT",
                rationale="Best combined quality and trend signal in the sample data.",
                urgency="this_month",
            )
        ],
        macro_outlook=(
            "Dry-run outlook: keep position sizing moderate until real macro data is connected."
        ),
        opportunities_spotted=[
            Opportunity(
                ticker="VTI",
                why_interesting="Broad-market ETF can reduce single-name concentration risk.",
            )
        ],
    )


def run_dry_run(settings: Settings) -> tuple[Path, Path]:
    """Generate local JSON and HTML artifacts without live external services."""

    output_dir = settings.report_output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis = build_sample_analysis()
    portfolio_value = f"100,000 {settings.portfolio_currency}"
    report_html = build_daily_report_html(
        analysis,
        portfolio_value=portfolio_value,
    )

    analysis_path = output_dir / "dry-run-analysis.json"
    report_path = output_dir / "dry-run-report.html"

    analysis_path.write_text(
        json.dumps(analysis.model_dump(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(report_html, encoding="utf-8")

    return analysis_path, report_path
