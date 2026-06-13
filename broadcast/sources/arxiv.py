import time, httpx, feedparser

_UA = "ParallightLab/2 (agent course; mailto:lab@parallight.ai)"
_client = httpx.Client(headers={"User-Agent": _UA}, timeout=30, follow_redirects=True)
_last = [0.0]

def _polite():
    dt = time.time() - _last[0]
    if dt < 3:
        time.sleep(3 - dt)
    _last[0] = time.time()

def fetch(cfg):
    cats = cfg["interests"]["arxiv_categories"]
    n = cfg["sources"]["arxiv"]["max_results"]
    q = "+OR+".join(f"cat:{c}" for c in cats)
    url = f"https://export.arxiv.org/api/query?search_query={q}&sortBy=submittedDate&sortOrder=descending&max_results={n}"
    _polite()
    r = _client.get(url)
    r.raise_for_status()
    feed = feedparser.parse(r.text)
    return [{"source": "arXiv", "title": " ".join(e.title.split()), "url": getattr(e, "id", ""), "meta": {"abstract": " ".join(e.summary.split())}} for e in feed.entries]
