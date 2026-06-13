import os, smtplib
from email.mime.text import MIMEText
from email.header import Header

def push(title, markdown):
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = (os.environ.get("GMAIL_ADDRESS") or "").strip()
    pw = (os.environ.get("GMAIL_APP_PASSWORD") or "").strip()
    to = (os.environ.get("MAIL_TO") or user).strip()
    if not (user and pw):
        return {"ok": False, "reason": "GMAIL_ADDRESS / GMAIL_APP_PASSWORD not set"}
    msg = MIMEText(markdown, "plain", "utf-8")
    msg["Subject"] = Header(title, "utf-8")
    msg["From"] = user
    msg["To"] = to
    try:
        with smtplib.SMTP(host, port, timeout=25) as s:
            s.starttls()
            s.login(user, pw)
            s.sendmail(user, [to], msg.as_string())
    except Exception as e:
        return {"ok": False, "reason": str(e)}
    return {"ok": True, "to": to}
