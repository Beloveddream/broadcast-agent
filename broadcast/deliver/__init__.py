from . import mailer, feishu

def deliver(channel, title, body):
    if channel in ("gmail", "email", "smtp"):
        return mailer.push(title, body)
    if channel == "feishu":
        return feishu.push(title, body)
    if channel == "local":
        return {"ok": True, "channel": "local"}
    return {"ok": False, "reason": f"unknown channel: {channel}"}
