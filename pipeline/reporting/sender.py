from pathlib import Path
from typing import Protocol

from pydantic import BaseModel

from pipeline.config import Settings


class EmailSendResult(BaseModel):
    id: str | None = None
    raw: dict[str, object]


class EmailClient(Protocol):
    def send(self, params: dict[str, object]) -> dict[str, object]: ...


class ResendEmailClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, params: dict[str, object]) -> dict[str, object]:
        import resend

        resend.api_key = self.api_key
        response = resend.Emails.send(params)
        return dict(response)


def send_html_report(
    *,
    settings: Settings,
    html: str,
    subject: str,
    client: EmailClient | None = None,
) -> EmailSendResult:
    if not settings.resend_api_key and client is None:
        raise ValueError("RESEND_API_KEY is required to send email")
    if not settings.report_email_to:
        raise ValueError("REPORT_EMAIL_TO is required to send email")
    if not settings.report_email_from:
        raise ValueError("REPORT_EMAIL_FROM is required to send email")

    email_client = client or ResendEmailClient(settings.resend_api_key or "")
    response = email_client.send(
        {
            "from": settings.report_email_from,
            "to": [settings.report_email_to],
            "subject": subject,
            "html": html,
        }
    )
    return EmailSendResult(id=response.get("id"), raw=response)


def send_report_file(
    *,
    settings: Settings,
    report_path: Path,
    subject: str = "Personal Quant Daily Report",
    client: EmailClient | None = None,
) -> EmailSendResult:
    return send_html_report(
        settings=settings,
        html=report_path.read_text(encoding="utf-8"),
        subject=subject,
        client=client,
    )
