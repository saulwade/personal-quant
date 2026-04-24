from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or .env."""

    database_url: str | None = None
    fred_api_key: str | None = None
    newsapi_key: str | None = None
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4"
    openai_fallback_model: str = "gpt-5.4-mini"
    openai_max_output_tokens: int = 6000
    resend_api_key: str | None = None
    report_email_to: str | None = None
    report_email_from: str | None = None
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_user_agent: str = "quant-personal/1.0"
    portfolio_currency: str = "MXN"
    timezone: str = "America/Monterrey"
    report_output_dir: Path = Path("reports")
    market_output_dir: Path = Path("data/market")
    portfolio_path: Path = Path("data/portfolio/positions.json")
    require_live_secrets: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_live_secrets(self) -> Self:
        if not self.require_live_secrets:
            return self

        missing = [
            name
            for name, value in {
                "DATABASE_URL": self.database_url,
                "OPENAI_API_KEY": self.openai_api_key,
                "RESEND_API_KEY": self.resend_api_key,
                "REPORT_EMAIL_TO": self.report_email_to,
                "REPORT_EMAIL_FROM": self.report_email_from,
            }.items()
            if not value
        ]
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Missing required live settings: {joined}")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
