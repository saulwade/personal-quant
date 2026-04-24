import pytest
from pydantic import ValidationError

from pipeline.config import Settings


def test_settings_defaults_for_local_dry_run() -> None:
    settings = Settings(_env_file=None)

    assert settings.openai_model == "gpt-5.4"
    assert settings.openai_fallback_model == "gpt-5.4-mini"
    assert settings.timezone == "America/Monterrey"
    assert settings.portfolio_currency == "MXN"
    assert str(settings.portfolio_path) == "data/portfolio/positions.json"


def test_live_settings_validation_lists_missing_required_values() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, require_live_secrets=True)

    message = str(exc_info.value)
    assert "DATABASE_URL" in message
    assert "OPENAI_API_KEY" in message
    assert "RESEND_API_KEY" in message
