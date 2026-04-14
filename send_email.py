"""
Email sender — converts the markdown report to HTML and sends it via Gmail SMTP.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date


def markdown_to_html(md: str) -> str:
    """Minimal markdown → HTML conversion (no external deps required)."""
    try:
        import re

        html_lines = []
        for line in md.split("\n"):
            # Headers
            if line.startswith("### "):
                line = f"<h3>{line[4:]}</h3>"
            elif line.startswith("## "):
                line = f"<h2>{line[3:]}</h2>"
            elif line.startswith("# "):
                line = f"<h1>{line[2:]}</h1>"
            # Horizontal rule
            elif line.strip() == "---":
                line = "<hr>"
            # Bold
            line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
            # Italic
            line = re.sub(r"\*(.+?)\*", r"<em>\1</em>", line)
            # Table rows (simple passthrough — keep as-is inside <pre>)
            html_lines.append(line)

        body = "<br>\n".join(html_lines)
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; max-width: 900px; margin: auto; padding: 20px; }}
  h1 {{ color: #1a1a2e; }} h2 {{ color: #16213e; border-bottom: 2px solid #0f3460; }}
  h3 {{ color: #0f3460; }} hr {{ border: 1px solid #e0e0e0; margin: 20px 0; }}
  strong {{ color: #e94560; }} table {{ border-collapse: collapse; width: 100%; }}
  td, th {{ border: 1px solid #ddd; padding: 8px; }} th {{ background: #f2f2f2; }}
</style>
</head>
<body>{body}</body>
</html>"""
    except Exception:
        # Fallback: plain text wrapped in <pre>
        return f"<html><body><pre>{md}</pre></body></html>"


def send_report(subject: str, report_md: str) -> None:
    """Send the report via Gmail SMTP using an App Password."""
    sender = os.environ["GMAIL_SENDER"]          # e.g. yourname@gmail.com
    app_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]    # zsp517013@gmail.com

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    # Plain-text fallback
    msg.attach(MIMEText(report_md, "plain", "utf-8"))
    # HTML version
    msg.attach(MIMEText(markdown_to_html(report_md), "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"Report sent to {recipient}")


if __name__ == "__main__":
    today = date.today().strftime("%Y-%m-%d")
    with open("report_output.md", encoding="utf-8") as f:
        report_md = f.read()

    subject = f"AI Intelligence Daily | AI 智能日報 — {today}"
    send_report(subject, report_md)
