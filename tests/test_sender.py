from pipeline.config import Settings
from pipeline.reporting.sender import send_html_report, send_report_file


class FakeEmailClient:
    def __init__(self):
        self.params = None

    def send(self, params):
        self.params = params
        return {"id": "email_123"}


def test_send_html_report_uses_resend_parameters() -> None:
    client = FakeEmailClient()
    settings = Settings(
        _env_file=None,
        resend_api_key="test-key",
        report_email_to="to@example.com",
        report_email_from="from@example.com",
    )

    result = send_html_report(
        settings=settings,
        html="<p>Hello</p>",
        subject="Test",
        client=client,
    )

    assert result.id == "email_123"
    assert client.params == {
        "from": "from@example.com",
        "to": ["to@example.com"],
        "subject": "Test",
        "html": "<p>Hello</p>",
    }


def test_send_report_file_reads_html(tmp_path) -> None:
    client = FakeEmailClient()
    report = tmp_path / "report.html"
    report.write_text("<h1>Report</h1>", encoding="utf-8")
    settings = Settings(
        _env_file=None,
        resend_api_key="test-key",
        report_email_to="to@example.com",
        report_email_from="from@example.com",
    )

    send_report_file(settings=settings, report_path=report, subject="Subject", client=client)

    assert client.params["html"] == "<h1>Report</h1>"


def test_send_html_report_requires_email_config() -> None:
    settings = Settings(_env_file=None, resend_api_key="test-key")

    try:
        send_html_report(settings=settings, html="<p>Hello</p>", subject="Test")
    except ValueError as exc:
        assert "REPORT_EMAIL_TO" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
