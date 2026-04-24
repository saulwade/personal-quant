from html import escape

from pipeline.agent.schemas import InvestmentAnalysis, RiskAlert


def _risk_color(alert: RiskAlert) -> str:
    return {
        "high": "#b42318",
        "medium": "#b54708",
        "low": "#027a48",
    }[alert.severity]


def build_daily_report_html(analysis: InvestmentAnalysis, *, portfolio_value: str = "N/A") -> str:
    """Render a simple Gmail-compatible HTML report."""

    risk_rows = "\n".join(f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee;color:{_risk_color(alert)};">
            {escape(alert.severity.upper())}
          </td>
          <td style="padding:8px;border-bottom:1px solid #eee;">{escape(alert.type)}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;">{escape(alert.description)}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;">
            {escape(alert.suggested_action)}
          </td>
        </tr>
        """ for alert in analysis.risk_alerts)
    if not risk_rows:
        risk_rows = """
        <tr>
          <td colspan="4" style="padding:8px;border-bottom:1px solid #eee;">
            No active risk alerts.
          </td>
        </tr>
        """

    adjustment_rows = "\n".join(f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #eee;">{escape(item.ticker)}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;">{escape(item.action)}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;">{escape(item.urgency)}</td>
          <td style="padding:8px;border-bottom:1px solid #eee;">{escape(item.rationale)}</td>
        </tr>
        """ for item in analysis.portfolio_adjustments)

    ticker_cards = "\n".join(f"""
        <div style="border:1px solid #e5e7eb;border-radius:8px;padding:14px;margin:12px 0;">
          <h3 style="margin:0 0 8px 0;font-size:16px;color:#111827;">{escape(item.ticker)}</h3>
          <p style="margin:4px 0;"><strong>Action:</strong> {escape(item.action)}
            ({escape(item.confidence)} confidence)</p>
          <p style="margin:4px 0;"><strong>Technical:</strong> {escape(item.technical_view)}</p>
          <p style="margin:4px 0;"><strong>Fundamental:</strong> {escape(item.fundamental_view)}</p>
          <p style="margin:4px 0;"><strong>Sentiment:</strong> {escape(item.sentiment_view)}</p>
          <p style="margin:4px 0;"><strong>Thesis:</strong> {escape(item.integrated_thesis)}</p>
        </div>
        """ for item in analysis.ticker_analyses)

    watchlist_items = "\n".join(f"""
        <li style="margin:8px 0;">
          <strong>{escape(item.ticker)}:</strong> {escape(item.thesis)}
          <br><span style="color:#4b5563;">Trigger: {escape(item.entry_trigger)}</span>
        </li>
        """ for item in analysis.watchlist_updates)
    if not watchlist_items:
        watchlist_items = "<li>No watchlist updates.</li>"

    return f"""<!doctype html>
<html>
  <body style="margin:0;background:#f9fafb;font-family:Arial,Helvetica,sans-serif;color:#111827;">
    <div style="max-width:760px;margin:0 auto;padding:24px;">
      <div style="background:#111827;color:#fff;padding:18px;border-radius:8px;">
        <h1 style="margin:0;font-size:22px;">Personal Quant Daily Report</h1>
        <p style="margin:8px 0 0 0;color:#d1d5db;">Portfolio value: {escape(portfolio_value)}</p>
      </div>

      <h2 style="font-size:18px;margin:24px 0 8px 0;">Risk Alerts</h2>
      <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #eee;">
        <tr>
          <th align="left" style="padding:8px;border-bottom:1px solid #eee;">Severity</th>
          <th align="left" style="padding:8px;border-bottom:1px solid #eee;">Type</th>
          <th align="left" style="padding:8px;border-bottom:1px solid #eee;">Description</th>
          <th align="left" style="padding:8px;border-bottom:1px solid #eee;">Action</th>
        </tr>
        {risk_rows}
      </table>

      <h2 style="font-size:18px;margin:24px 0 8px 0;">Macro Context</h2>
      <p style="background:#fff;border:1px solid #eee;padding:12px;border-radius:8px;">
        {escape(analysis.market_summary)}
      </p>

      <h2 style="font-size:18px;margin:24px 0 8px 0;">Recommended Actions</h2>
      <table style="width:100%;border-collapse:collapse;background:#fff;border:1px solid #eee;">
        <tr>
          <th align="left" style="padding:8px;border-bottom:1px solid #eee;">Ticker</th>
          <th align="left" style="padding:8px;border-bottom:1px solid #eee;">Action</th>
          <th align="left" style="padding:8px;border-bottom:1px solid #eee;">Urgency</th>
          <th align="left" style="padding:8px;border-bottom:1px solid #eee;">Rationale</th>
        </tr>
        {adjustment_rows}
      </table>

      <h2 style="font-size:18px;margin:24px 0 8px 0;">Ticker Analysis</h2>
      {ticker_cards}

      <h2 style="font-size:18px;margin:24px 0 8px 0;">Watchlist</h2>
      <ul
        style="background:#fff;border:1px solid #eee;padding:12px 12px 12px 32px;border-radius:8px;"
      >
        {watchlist_items}
      </ul>

      <h2 style="font-size:18px;margin:24px 0 8px 0;">Portfolio Health</h2>
      <p style="background:#fff;border:1px solid #eee;padding:12px;border-radius:8px;">
        <strong>Score:</strong> {analysis.portfolio_health.overall_score}/100<br>
        {escape(analysis.portfolio_health.commentary)}<br>
        <span style="color:#4b5563;">
          {escape(analysis.portfolio_health.diversification_notes)}
        </span>
      </p>
    </div>
  </body>
</html>
"""
