from decimal import Decimal

from pipeline.portfolio import (
    Position,
    empty_portfolio,
    init_portfolio,
    load_portfolio,
    portfolio_context,
    remove_position,
    save_portfolio,
    upsert_position,
)


def test_init_portfolio_creates_empty_file(tmp_path) -> None:
    path = tmp_path / "positions.json"

    portfolio = init_portfolio(path, base_currency="MXN")
    loaded = load_portfolio(path, base_currency="MXN")

    assert portfolio.is_empty
    assert loaded.base_currency == "MXN"
    assert loaded.positions == []


def test_upsert_and_remove_position() -> None:
    portfolio = empty_portfolio(base_currency="MXN")
    position = Position(
        ticker="voo",
        shares=Decimal("1.5"),
        avg_buy_price=Decimal("500"),
        currency="USD",
    )

    upsert_position(portfolio, position)
    assert portfolio.positions[0].ticker == "VOO"

    removed = remove_position(portfolio, "VOO")
    assert removed is True
    assert portfolio.is_empty


def test_portfolio_context_summarizes_cost_by_currency(tmp_path) -> None:
    portfolio = empty_portfolio(base_currency="MXN")
    upsert_position(
        portfolio,
        Position(ticker="MSFT", shares=Decimal("2"), avg_buy_price=Decimal("300")),
    )
    save_portfolio(portfolio, tmp_path / "positions.json")

    context = portfolio_context(portfolio)

    assert context["is_empty"] is False
    assert context["position_count"] == 1
    assert context["total_cost_by_currency"]["USD"] == "600"
