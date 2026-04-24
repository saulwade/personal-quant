from pipeline import cli
from pipeline.config import Settings


def test_portfolio_cli_init_add_show_remove(tmp_path, monkeypatch) -> None:
    portfolio_path = tmp_path / "positions.json"

    def fake_settings() -> Settings:
        return Settings(_env_file=None, portfolio_path=portfolio_path)

    monkeypatch.setattr(cli, "Settings", fake_settings)

    assert cli.main(["portfolio", "init"]) == 0
    assert portfolio_path.exists()

    assert (
        cli.main(
            [
                "portfolio",
                "add",
                "--ticker",
                "VOO",
                "--shares",
                "1",
                "--avg-buy-price",
                "500",
            ]
        )
        == 0
    )
    assert cli.main(["portfolio", "show"]) == 0
    assert cli.main(["portfolio", "remove", "--ticker", "VOO"]) == 0
