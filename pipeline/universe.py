from typing import Literal

from pydantic import BaseModel

AssetClass = Literal["equity", "etf", "cash_proxy", "crypto_proxy"]
Market = Literal["us", "mexico", "global", "cash"]
RiskBucket = Literal["core", "growth", "aggressive", "defensive", "cash"]


class UniverseAsset(BaseModel):
    ticker: str
    name: str
    asset_class: AssetClass
    market: Market
    risk_bucket: RiskBucket
    role: str


GBM_GROWTH_UNIVERSE: tuple[UniverseAsset, ...] = (
    UniverseAsset(
        ticker="VOO",
        name="Vanguard S&P 500 ETF",
        asset_class="etf",
        market="us",
        risk_bucket="core",
        role="US large-cap core exposure",
    ),
    UniverseAsset(
        ticker="VTI",
        name="Vanguard Total Stock Market ETF",
        asset_class="etf",
        market="us",
        risk_bucket="core",
        role="Broad US equity market exposure",
    ),
    UniverseAsset(
        ticker="QQQ",
        name="Invesco QQQ Trust",
        asset_class="etf",
        market="us",
        risk_bucket="growth",
        role="US growth and Nasdaq-100 exposure",
    ),
    UniverseAsset(
        ticker="VT",
        name="Vanguard Total World Stock ETF",
        asset_class="etf",
        market="global",
        risk_bucket="core",
        role="Global equity diversification",
    ),
    UniverseAsset(
        ticker="AAPL",
        name="Apple",
        asset_class="equity",
        market="us",
        risk_bucket="growth",
        role="Large-cap quality technology",
    ),
    UniverseAsset(
        ticker="MSFT",
        name="Microsoft",
        asset_class="equity",
        market="us",
        risk_bucket="growth",
        role="Large-cap software and cloud quality",
    ),
    UniverseAsset(
        ticker="NVDA",
        name="NVIDIA",
        asset_class="equity",
        market="us",
        risk_bucket="aggressive",
        role="AI semiconductor growth exposure",
    ),
    UniverseAsset(
        ticker="GOOGL",
        name="Alphabet",
        asset_class="equity",
        market="us",
        risk_bucket="growth",
        role="Search, ads, cloud, and AI platform exposure",
    ),
    UniverseAsset(
        ticker="AMZN",
        name="Amazon",
        asset_class="equity",
        market="us",
        risk_bucket="growth",
        role="E-commerce, cloud, and logistics growth exposure",
    ),
    UniverseAsset(
        ticker="META",
        name="Meta Platforms",
        asset_class="equity",
        market="us",
        risk_bucket="aggressive",
        role="Digital advertising, social, and AI exposure",
    ),
    UniverseAsset(
        ticker="BRK-B",
        name="Berkshire Hathaway",
        asset_class="equity",
        market="us",
        risk_bucket="defensive",
        role="Quality compounder and diversified business exposure",
    ),
    UniverseAsset(
        ticker="COST",
        name="Costco",
        asset_class="equity",
        market="us",
        risk_bucket="defensive",
        role="Defensive consumer quality exposure",
    ),
    UniverseAsset(
        ticker="JPM",
        name="JPMorgan Chase",
        asset_class="equity",
        market="us",
        risk_bucket="defensive",
        role="Large-cap financial sector exposure",
    ),
    UniverseAsset(
        ticker="NAFTRAC.MX",
        name="NAFTRAC",
        asset_class="etf",
        market="mexico",
        risk_bucket="core",
        role="Mexican equity index exposure",
    ),
    UniverseAsset(
        ticker="FEMSAUBD.MX",
        name="FEMSA",
        asset_class="equity",
        market="mexico",
        risk_bucket="defensive",
        role="Mexican consumer and beverage exposure",
    ),
    UniverseAsset(
        ticker="GMEXICOB.MX",
        name="Grupo Mexico",
        asset_class="equity",
        market="mexico",
        risk_bucket="aggressive",
        role="Mexican mining and infrastructure exposure",
    ),
    UniverseAsset(
        ticker="WALMEX.MX",
        name="Walmart de Mexico",
        asset_class="equity",
        market="mexico",
        risk_bucket="defensive",
        role="Mexican consumer staples exposure",
    ),
)


UNIVERSES: dict[str, tuple[UniverseAsset, ...]] = {
    "gbm-growth": GBM_GROWTH_UNIVERSE,
}


def get_universe(name: str) -> tuple[UniverseAsset, ...]:
    try:
        return UNIVERSES[name]
    except KeyError as exc:
        available = ", ".join(sorted(UNIVERSES))
        raise ValueError(f"Unknown universe '{name}'. Available universes: {available}") from exc


def universe_by_ticker(name: str) -> dict[str, UniverseAsset]:
    return {asset.ticker: asset for asset in get_universe(name)}
