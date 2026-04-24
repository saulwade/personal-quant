from typing import Any

from pipeline.data.market import MarketAssetSnapshot, MarketUniverseSnapshot


def _asset_context(asset: MarketAssetSnapshot) -> dict[str, Any]:
    return {
        "ticker": asset.ticker,
        "name": asset.name,
        "asset_class": asset.asset_class,
        "market": asset.market,
        "risk_bucket": asset.risk_bucket,
        "role": asset.role,
        "years_requested": asset.years_requested,
        "start_date": asset.start_date,
        "end_date": asset.end_date,
        "observations": asset.observations,
        "metrics": asset.metrics,
        "opportunity_score": asset.opportunity_score,
        "risk_score": asset.risk_score,
        "warnings": asset.warnings,
    }


def build_openai_market_context(
    snapshot: MarketUniverseSnapshot,
    *,
    portfolio: dict[str, Any] | None = None,
) -> dict[str, Any]:
    valid_assets = [asset for asset in snapshot.assets if asset.observations > 0]
    sorted_by_opportunity = sorted(
        valid_assets,
        key=lambda asset: asset.opportunity_score or 0,
        reverse=True,
    )
    sorted_by_risk = sorted(
        valid_assets,
        key=lambda asset: asset.risk_score or 0,
        reverse=True,
    )

    return {
        "investor_profile": {
            "platform": "GBM",
            "country": "Mexico",
            "base_currency": "MXN",
            "objective": "long-term wealth growth",
            "risk_profile": "long_term_growth_aggressive",
            "experience": "beginner investor studying finance",
        },
        "data_status": {
            "market_snapshot_generated_at": snapshot.generated_at,
            "years_requested": snapshot.years_requested,
            "valid_assets": len(valid_assets),
            "warnings": snapshot.warnings,
            "missing_context": [
                "real portfolio positions",
                "fundamental analysis",
                "news sentiment",
                "macro indicators",
                "tax constraints",
            ],
        },
        "portfolio": portfolio
        or {
            "is_empty": True,
            "position_count": 0,
            "note": "No real GBM positions have been added yet.",
        },
        "top_opportunity_screen": [_asset_context(asset) for asset in sorted_by_opportunity[:8]],
        "highest_risk_screen": [_asset_context(asset) for asset in sorted_by_risk[:5]],
        "all_assets": [_asset_context(asset) for asset in valid_assets],
        "instruction": (
            "Produce a structured investment analysis in Spanish. Treat these data as "
            "a quant screening layer, not as complete investment advice. Identify "
            "research candidates, risk alerts, watchlist updates, and cautious portfolio "
            "adjustments for a long-term aggressive beginner using GBM."
        ),
    }
