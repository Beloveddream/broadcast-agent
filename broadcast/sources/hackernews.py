import httpx

_client = httpx.Client(timeout=30, follow_redirects=True)

def fetch(cfg):
    c = cfg["sources"]["hackernews"]
    kws = cfg["interests"]["keywords"]
    params = {"tags": "story", "query": " ".join(kws[:3]), "numericFilters": f"points>{c['min_points']}", "hitsPerPage": c["top_n"]}
    r = _client.get("https://hn.algolia.com/api/v1/search_by_date", params=params)
    r.raise_for_status()
    return [{"source": "Hacker News", "title": h.get("title") or "(no title)", "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}", "meta": {"points": h.get("points")}} for h in r.json().get("hits", [])]
