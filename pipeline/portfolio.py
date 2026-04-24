import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, Field


class Position(BaseModel):
    ticker: str
    shares: Decimal = Field(gt=0)
    avg_buy_price: Decimal = Field(gt=0)
    currency: str = "USD"
    asset_type: str = "equity"
    notes: str | None = None


class Portfolio(BaseModel):
    base_currency: str = "MXN"
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    positions: list[Position] = Field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return len(self.positions) == 0


def empty_portfolio(*, base_currency: str = "MXN") -> Portfolio:
    now = datetime.now(UTC).isoformat()
    return Portfolio(base_currency=base_currency, created_at=now, updated_at=now, positions=[])


def load_portfolio(path: Path, *, base_currency: str = "MXN") -> Portfolio:
    if not path.exists():
        return empty_portfolio(base_currency=base_currency)
    return Portfolio.model_validate_json(path.read_text(encoding="utf-8"))


def save_portfolio(portfolio: Portfolio, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    portfolio.updated_at = datetime.now(UTC).isoformat()
    path.write_text(
        json.dumps(portfolio.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def init_portfolio(path: Path, *, base_currency: str = "MXN", force: bool = False) -> Portfolio:
    if path.exists() and not force:
        return load_portfolio(path, base_currency=base_currency)
    portfolio = empty_portfolio(base_currency=base_currency)
    save_portfolio(portfolio, path)
    return portfolio


def upsert_position(portfolio: Portfolio, position: Position) -> Portfolio:
    normalized_ticker = position.ticker.upper()
    position.ticker = normalized_ticker
    remaining = [item for item in portfolio.positions if item.ticker.upper() != normalized_ticker]
    portfolio.positions = [*remaining, position]
    portfolio.updated_at = datetime.now(UTC).isoformat()
    return portfolio


def remove_position(portfolio: Portfolio, ticker: str) -> bool:
    normalized_ticker = ticker.upper()
    original_count = len(portfolio.positions)
    portfolio.positions = [
        position for position in portfolio.positions if position.ticker.upper() != normalized_ticker
    ]
    portfolio.updated_at = datetime.now(UTC).isoformat()
    return len(portfolio.positions) != original_count


def portfolio_context(portfolio: Portfolio) -> dict[str, object]:
    total_cost_by_currency: dict[str, str] = {}
    for position in portfolio.positions:
        cost = position.shares * position.avg_buy_price
        current = Decimal(total_cost_by_currency.get(position.currency, "0"))
        total_cost_by_currency[position.currency] = str(current + cost)

    return {
        "base_currency": portfolio.base_currency,
        "is_empty": portfolio.is_empty,
        "position_count": len(portfolio.positions),
        "total_cost_by_currency": total_cost_by_currency,
        "positions": [position.model_dump(mode="json") for position in portfolio.positions],
    }
