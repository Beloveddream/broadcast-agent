import httpx
from bs4 import BeautifulSoup

_client = httpx.Client(timeout=30, headers={"User-Agent": "ParallightLab/2"}, follow_redirects=True)

def fetch(cfg):
    c = cfg["sources"]["github_trending"]
    lang = c.get("language", "")
    since = c.get("since", "daily")
    n = c.get("top_n", 10)
    url = f"https://github.com/trending/{lang}?since={since}" if lang else f"https://github.com/trending?since={since}"
    r = _client.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items = []
    for art in soup.select("article.Box-row")[:n]:
        a = art.select_one("h2 a")
        if not a:
            continue
        href = "https://github.com" + a.get("href", "")
        desc_el = art.select_one("p")
        stars_el = art.select_one("span.d-inline-block.float-sm-right")
        items.append({"source": "GitHub Trending", "title": " ".join(a.get_text().split()), "url": href, "meta": {"desc": desc_el.get_text(strip=True) if desc_el else "", "stars_today": " ".join(stars_el.get_text().split()) if stars_el else ""}})
    return items
