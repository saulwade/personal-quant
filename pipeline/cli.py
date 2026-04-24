import argparse
from collections.abc import Sequence
from pathlib import Path

from loguru import logger

from pipeline.config import Settings
from pipeline.data.market import build_market_snapshot, write_market_snapshot
from pipeline.dry_run import run_dry_run
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

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "daily" and args.dry_run:
        settings = Settings()
        analysis_path, report_path = run_dry_run(settings)
        logger.info("Dry-run analysis written to {}", analysis_path)
        logger.info("Dry-run report written to {}", report_path)
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

    parser.error("Unsupported command.")
    return 2
