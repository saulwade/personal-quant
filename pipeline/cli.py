import argparse
from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path

from loguru import logger

from pipeline.config import Settings
from pipeline.data.market import build_market_snapshot, write_market_snapshot
from pipeline.dry_run import run_dry_run
from pipeline.portfolio import (
    Position,
    init_portfolio,
    load_portfolio,
    portfolio_context,
    remove_position,
    save_portfolio,
    upsert_position,
)
from pipeline.reporting.sender import send_report_file
from pipeline.universe import UNIVERSES, get_universe, universe_by_ticker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quant", description="Personal Quant pipeline CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    daily = subparsers.add_parser("daily", help="Run the daily analysis pipeline")
    daily.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate local sample artifacts without live APIs, database, or email.",
    )
    daily.add_argument(
        "--market-snapshot",
        type=Path,
        help="Optional market snapshot JSON to power the dry-run report.",
    )
    daily.add_argument(
        "--use-openai",
        action="store_true",
        help="Use OpenAI to synthesize the dry-run report from --market-snapshot.",
    )
    daily.add_argument(
        "--send-email",
        action="store_true",
        help="Send the generated report through Resend.",
    )

    market = subparsers.add_parser("market", help="Fetch and summarize market data")
    market.add_argument(
        "--universe",
        choices=sorted(UNIVERSES),
        default="gbm-growth",
        help="Named universe to analyze.",
    )
    market.add_argument(
        "--tickers",
        nargs="+",
        help="Optional explicit tickers. Defaults to all tickers in the selected universe.",
    )
    market.add_argument(
        "--years",
        type=int,
        default=5,
        help="Historical daily lookback in years.",
    )
    market.add_argument(
        "--output",
        help="Output JSON path. Defaults to data/market/<universe>-snapshot.json.",
    )

    portfolio = subparsers.add_parser("portfolio", help="Manage local portfolio positions")
    portfolio_subparsers = portfolio.add_subparsers(dest="portfolio_command", required=True)

    portfolio_init = portfolio_subparsers.add_parser("init", help="Create local portfolio file")
    portfolio_init.add_argument("--force", action="store_true", help="Overwrite existing file.")

    portfolio_subparsers.add_parser("show", help="Show local portfolio summary")

    portfolio_add = portfolio_subparsers.add_parser("add", help="Add or update a position")
    portfolio_add.add_argument("--ticker", required=True)
    portfolio_add.add_argument("--shares", required=True, type=Decimal)
    portfolio_add.add_argument("--avg-buy-price", required=True, type=Decimal)
    portfolio_add.add_argument("--currency", default="USD")
    portfolio_add.add_argument("--asset-type", default="equity")
    portfolio_add.add_argument("--notes")

    portfolio_remove = portfolio_subparsers.add_parser("remove", help="Remove a position")
    portfolio_remove.add_argument("--ticker", required=True)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "daily" and args.dry_run:
        settings = Settings()
        analysis_path, report_path = run_dry_run(
            settings,
            market_snapshot_path=args.market_snapshot,
            use_openai=args.use_openai,
        )
        logger.info("Dry-run analysis written to {}", analysis_path)
        logger.info("Dry-run report written to {}", report_path)
        if args.send_email:
            result = send_report_file(
                settings=settings,
                report_path=report_path,
            )
            logger.info("Email sent via Resend with id {}", result.id)
        return 0

    if args.command == "market":
        settings = Settings()
        universe_assets = universe_by_ticker(args.universe)
        tickers = args.tickers or [asset.ticker for asset in get_universe(args.universe)]
        output_path = (
            settings.market_output_dir / f"{args.universe}-snapshot.json"
            if args.output is None
            else Path(args.output)
        )
        snapshot = build_market_snapshot(
            tickers,
            years=args.years,
            universe_assets=universe_assets,
        )
        write_market_snapshot(snapshot, output_path)
        logger.info(
            "Market snapshot written to {} for {} assets",
            output_path,
            len(snapshot.assets),
        )
        if snapshot.warnings:
            logger.warning("Snapshot completed with {} warnings", len(snapshot.warnings))
        return 0

    if args.command == "portfolio":
        settings = Settings()
        path = settings.portfolio_path

        if args.portfolio_command == "init":
            portfolio = init_portfolio(
                path,
                base_currency=settings.portfolio_currency,
                force=args.force,
            )
            logger.info(
                "Portfolio initialized at {} with {} positions",
                path,
                len(portfolio.positions),
            )
            return 0

        portfolio = load_portfolio(path, base_currency=settings.portfolio_currency)

        if args.portfolio_command == "show":
            context = portfolio_context(portfolio)
            logger.info("Portfolio path: {}", path)
            logger.info("Base currency: {}", context["base_currency"])
            logger.info("Positions: {}", context["position_count"])
            if portfolio.is_empty:
                logger.info("Portfolio is empty. Add positions after your first GBM purchase.")
            for position in portfolio.positions:
                logger.info(
                    "{} | shares={} | avg_buy_price={} {} | asset_type={}",
                    position.ticker,
                    position.shares,
                    position.avg_buy_price,
                    position.currency,
                    position.asset_type,
                )
            return 0

        if args.portfolio_command == "add":
            position = Position(
                ticker=args.ticker,
                shares=args.shares,
                avg_buy_price=args.avg_buy_price,
                currency=args.currency.upper(),
                asset_type=args.asset_type,
                notes=args.notes,
            )
            upsert_position(portfolio, position)
            save_portfolio(portfolio, path)
            logger.info("Saved position {} to {}", position.ticker, path)
            return 0

        if args.portfolio_command == "remove":
            removed = remove_position(portfolio, args.ticker)
            save_portfolio(portfolio, path)
            if removed:
                logger.info("Removed position {}", args.ticker.upper())
            else:
                logger.warning("Position {} was not present", args.ticker.upper())
            return 0

    parser.error("Unsupported command.")
    return 2
