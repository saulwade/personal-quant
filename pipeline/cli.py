import argparse
from collections.abc import Sequence

from loguru import logger

from pipeline.config import Settings
from pipeline.dry_run import run_dry_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quant", description="Personal Quant pipeline CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    daily = subparsers.add_parser("daily", help="Run the daily analysis pipeline")
    daily.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate local sample artifacts without live APIs, database, or email.",
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

    parser.error("Only `quant daily --dry-run` is implemented in this sprint.")
    return 2
