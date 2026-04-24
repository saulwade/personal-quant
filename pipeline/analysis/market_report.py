from pipeline.agent.schemas import (
    InvestmentAnalysis,
    Opportunity,
    PortfolioAdjustment,
    PortfolioHealth,
    RiskAlert,
    TickerAnalysis,
    WatchlistUpdate,
)
from pipeline.data.market import MarketAssetSnapshot, MarketUniverseSnapshot


def _number(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None


def _format_pct(value: object) -> str:
    number = _number(value)
    if number is None:
        return "n/a"
    return f"{number:.2f}%"


def _top_assets(
    assets: list[MarketAssetSnapshot],
    field: str,
    *,
    reverse: bool = True,
    limit: int = 3,
) -> list[MarketAssetSnapshot]:
    scored = [asset for asset in assets if _number(getattr(asset, field)) is not None]
    return sorted(
        scored,
        key=lambda asset: _number(getattr(asset, field)) or 0,
        reverse=reverse,
    )[:limit]


def _action_for_asset(asset: MarketAssetSnapshot) -> tuple[str, str, str]:
    opportunity = asset.opportunity_score
    risk = asset.risk_score
    trend = asset.metrics.get("trend")

    if opportunity is None or risk is None:
        return (
            "watch",
            "Insufficient data for a stronger mechanical signal.",
            "low",
        )

    if opportunity >= 72 and risk <= 70 and trend == "uptrend":
        return (
            "watch",
            "Strong mechanical setup; candidate for deeper AI and fundamental review.",
            "medium",
        )
    if risk >= 75:
        return (
            "watch",
            "Risk is elevated, so this should stay on watch instead of becoming a buy signal.",
            "medium",
        )
    if trend == "downtrend":
        return (
            "watch",
            "Trend is weak; wait for stabilization before considering entry.",
            "medium",
        )
    return (
        "watch",
        "Signal is mixed; keep monitoring until more evidence accumulates.",
        "low",
    )


def _technical_view(asset: MarketAssetSnapshot) -> str:
    metrics = asset.metrics
    return (
        f"Trend: {metrics.get('trend', 'n/a')}. "
        f"1M/3M/12M returns: {_format_pct(metrics.get('return_1m_pct'))}, "
        f"{_format_pct(metrics.get('return_3m_pct'))}, "
        f"{_format_pct(metrics.get('return_12m_pct'))}. "
        f"12-1 momentum: {_format_pct(metrics.get('momentum_12_1_pct'))}. "
        f"RSI 14: {metrics.get('rsi_14', 'n/a')}."
    )


def _forecast_view(asset: MarketAssetSnapshot) -> str:
    metrics = asset.metrics
    return (
        "No ML forecast is connected yet. Mechanical proxy uses trend, momentum, "
        f"12M volatility ({_format_pct(metrics.get('volatility_12m_pct'))}), "
        f"and max drawdown ({_format_pct(metrics.get('max_drawdown_pct'))})."
    )


def _risk_factors(asset: MarketAssetSnapshot) -> list[str]:
    factors: list[str] = []
    risk = asset.risk_score
    drawdown = _number(asset.metrics.get("max_drawdown_pct"))
    volatility = _number(asset.metrics.get("volatility_12m_pct"))

    if risk is not None and risk >= 75:
        factors.append("Elevated mechanical risk score")
    if drawdown is not None and drawdown <= -35:
        factors.append("Large historical drawdown")
    if volatility is not None and volatility >= 35:
        factors.append("High annualized volatility")
    if asset.risk_bucket == "aggressive":
        factors.append("Aggressive universe bucket")
    if asset.warnings:
        factors.extend(asset.warnings)

    return factors or ["No major mechanical risk flag in current snapshot"]


def build_mechanical_analysis(snapshot: MarketUniverseSnapshot) -> InvestmentAnalysis:
    valid_assets = [asset for asset in snapshot.assets if asset.observations > 0]
    top_opportunities = _top_assets(valid_assets, "opportunity_score", limit=3)
    highest_risk = _top_assets(valid_assets, "risk_score", limit=3)

    if top_opportunities:
        top_names = ", ".join(asset.ticker for asset in top_opportunities)
        market_summary = (
            f"Mechanical market snapshot across {len(valid_assets)} assets. "
            f"Top opportunity candidates by score: {top_names}. "
            "This is a quantitative screen, not a final investment recommendation."
        )
    else:
        market_summary = (
            "Mechanical market snapshot has no valid assets yet. "
            "Fetch market data before interpreting opportunities."
        )

    average_opportunity = (
        sum(asset.opportunity_score or 0 for asset in valid_assets) / len(valid_assets)
        if valid_assets
        else 0
    )
    average_risk = (
        sum(asset.risk_score or 0 for asset in valid_assets) / len(valid_assets)
        if valid_assets
        else 100
    )
    health_score = round(max(0, min(100, 55 + average_opportunity * 0.35 - average_risk * 0.2)))

    ticker_analyses: list[TickerAnalysis] = []
    for asset in valid_assets:
        action, action_reasoning, confidence = _action_for_asset(asset)
        ticker_analyses.append(
            TickerAnalysis(
                ticker=asset.ticker,
                technical_view=_technical_view(asset),
                fundamental_view=(
                    "Fundamental analysis is not connected yet; this view is market-data only."
                ),
                sentiment_view=(
                    "News and sentiment are not connected yet; this view is market-data only."
                ),
                forecast_view=_forecast_view(asset),
                integrated_thesis=(
                    f"{asset.role or 'Universe asset'} | opportunity score: "
                    f"{asset.opportunity_score}; risk score: {asset.risk_score}."
                ),
                action=action,
                action_reasoning=action_reasoning,
                confidence=confidence,
                risk_factors=_risk_factors(asset),
            )
        )

    watchlist_updates = [
        WatchlistUpdate(
            ticker=asset.ticker,
            thesis=(
                f"Opportunity score {asset.opportunity_score}; "
                f"risk score {asset.risk_score}; trend {asset.metrics.get('trend')}."
            ),
            entry_trigger=(
                "Promote to AI/fundamental review if momentum stays positive and "
                "risk score remains below 70."
            ),
        )
        for asset in top_opportunities
    ]

    risk_alerts = [
        RiskAlert(
            severity="high" if (asset.risk_score or 0) >= 80 else "medium",
            type="drawdown",
            description=(
                f"{asset.ticker} has risk score {asset.risk_score}, "
                f"12M volatility {_format_pct(asset.metrics.get('volatility_12m_pct'))}, "
                f"and max drawdown {_format_pct(asset.metrics.get('max_drawdown_pct'))}."
            ),
            suggested_action=(
                "Keep sizing small until AI, fundamentals, and news confirm the setup."
            ),
        )
        for asset in highest_risk
        if (asset.risk_score or 0) >= 60
    ]

    portfolio_adjustments = [
        PortfolioAdjustment(
            action="buy",
            ticker=asset.ticker,
            rationale=(
                f"Research candidate only: opportunity score {asset.opportunity_score}, "
                f"risk score {asset.risk_score}, trend {asset.metrics.get('trend')}."
            ),
            urgency="this_month",
        )
        for asset in top_opportunities
        if (asset.opportunity_score or 0) >= 70
    ]

    opportunities = [
        Opportunity(
            ticker=asset.ticker,
            why_interesting=(
                f"{asset.role or 'Universe asset'} with opportunity score "
                f"{asset.opportunity_score} and trend {asset.metrics.get('trend')}."
            ),
        )
        for asset in top_opportunities
    ]

    return InvestmentAnalysis(
        market_summary=market_summary,
        portfolio_health=PortfolioHealth(
            overall_score=health_score,
            commentary=(
                "This score describes the current research universe, not your real portfolio yet."
            ),
            diversification_notes=(
                "Universe includes broad ETFs, US growth, defensive compounders, "
                "and selected Mexican equities for GBM-oriented analysis."
            ),
        ),
        ticker_analyses=ticker_analyses,
        watchlist_updates=watchlist_updates,
        risk_alerts=risk_alerts,
        portfolio_adjustments=portfolio_adjustments,
        macro_outlook=(
            "Macro data is not connected yet. Current output is driven by market price behavior."
        ),
        opportunities_spotted=opportunities,
    )
