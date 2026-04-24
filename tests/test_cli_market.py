import json
from pathlib import Path

import pandas as pd

from pipeline import cli
from pipeline.data.market import build_market_snapshot


def make_history(days: int = 300) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=days, freq="B")
    return pd.DataFrame({"Close": [100 + value for value in range(days)]}, index=index)


def test_market_cli_writes_snapshot_with_mocked_downloader(
    tmp_path: Path,
    monkeypatch,
) -> None:
    def fake_build_market_snapshot(tickers, *, years, universe_assets):
        return build_market_snapshot(
            tickers,
            years=years,
            universe_assets=universe_assets,
            downloader=lambda ticker, requested_years: make_history(),
            request_pause_seconds=0,
        )

    monkeypatch.setattr(cli, "build_market_snapshot", fake_build_market_snapshot)

    output = tmp_path / "snapshot.json"
    exit_code = cli.main(
        [
            "market",
            "--universe",
            "gbm-growth",
            "--tickers",
            "VOO",
            "--years",
            "5",
            "--output",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["assets"][0]["ticker"] == "VOO"
