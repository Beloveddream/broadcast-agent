import os, re, datetime

DIGEST_PATH = os.path.join(os.path.dirname(__file__), "..", "digest.md")

def _key(line):
    m = re.search(r"https?://\S+", line)
    return m.group(0).rstrip(").,") if m else line.strip()

def load_seen():
    if not os.path.exists(DIGEST_PATH):
        return set()
    seen = set()
    with open(DIGEST_PATH, encoding="utf-8") as f:
        for line in f:
            if "http" in line:
                seen.add(_key(line))
    return seen

def dedup(summary_text, seen):
    kept = [ln for ln in summary_text.splitlines() if not ("http" in ln and _key(ln) in seen)]
    return "\n".join(kept).strip()

def append(title, body):
    stamp = datetime.date.today().isoformat()
    with open(DIGEST_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n\n## {stamp} · {title}\n\n{body}\n")

def history_compacted(max_chars=800):
    if not os.path.exists(DIGEST_PATH):
        return ""
    return open(DIGEST_PATH, encoding="utf-8").read()[-max_chars:]
