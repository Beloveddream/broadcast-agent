import os, time, hmac, hashlib, base64, httpx

def _sign(secret, ts):
    s = f"{ts}\n{secret}"
    return base64.b64encode(hmac.new(s.encode(), b"", hashlib.sha256).digest()).decode()

def push(title, markdown):
    url = (os.environ.get("FEISHU_WEBHOOK_URL") or "").strip()
    if not url:
        return {"ok": False, "reason": "FEISHU_WEBHOOK_URL not set"}
    payload = {"msg_type": "interactive", "card": {"schema": "2.0",
        "header": {"title": {"tag": "plain_text", "content": title}},
        "body": {"elements": [{"tag": "markdown", "content": markdown}]}}}
    secret = (os.environ.get("FEISHU_WEBHOOK_SECRET") or "").strip()
    if secret:
        ts = str(int(time.time()))
        payload["timestamp"] = ts
        payload["sign"] = _sign(secret, ts)
    try:
        r = httpx.post(url, json=payload, timeout=20)
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    except Exception as e:
        return {"ok": False, "reason": str(e)}
    return {"ok": data.get("code") == 0, "status": r.status_code, "resp": data}
