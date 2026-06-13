import os, re, sys, httpx, yaml
from dotenv import load_dotenv
from broadcast.sources import arxiv, hackernews, github_trending
from broadcast.summarize import summarize_source
from broadcast import digest, deliver
from broadcast.agent_llm import complete, text_of

load_dotenv()
CFG = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "config.yaml"), encoding="utf-8"))
SOURCES = {"arxiv": arxiv, "hackernews": hackernews, "github_trending": github_trending}
_full_client = httpx.Client(timeout=8, follow_redirects=True, headers={"User-Agent": "ParallightLab/2"})

def _full_page_text(url, limit=4000):
    try:
        r = _full_client.get(url)
        txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", r.text, flags=re.S|re.I)
        return " ".join(re.sub(r"<[^>]+>", " ", txt).split())[:limit]
    except Exception:
        return ""

def gather():
    out = {}
    for name, mod in SOURCES.items():
        if not CFG["sources"][name]["enabled"]:
            continue
        try:
            out[name] = mod.fetch(CFG)
            print(f"  · {name}: {len(out[name])} items")
        except Exception as e:
            print(f"  ⚠️  {name} failed: {e}")
    return out

def run_correct():
    print("📡 Fetching (lightweight only)...")
    items_by_source = gather()
    kws = CFG["interests"]["keywords"]
    budget = CFG["limits"]["per_source_summary_tokens"]
    sub_tokens = 0
    summaries = []
    for name, items in items_by_source.items():
        res = summarize_source(name, items, kws, budget)
        sub_tokens += res["usage"].input_tokens
        summaries.append(f"### {res['source']}\n{res['summary']}")
    joined = "\n\n".join(summaries)
    resp = complete([{"role": "user", "content": f"把这些各源摘要合成一份精炼的今日播报（去重、按重要性排序、每条带链接）：\n\n{joined}"}], max_tokens=1500)
    body = text_of(resp)
    print(f"\n🔬 isolation+jit — main input_tokens={resp.usage.input_tokens}, sub_tokens={sub_tokens}")
    seen = digest.load_seen()
    deduped = digest.dedup(body, seen)
    if deduped != body:
        print("   📎 deduped against digest.md")
    return deduped or body

def run_naive():
    print("📡 Fetching (naive: full page text)...")
    items_by_source = gather()
    blob = []
    budget = 12
    for name, items in items_by_source.items():
        for it in items:
            meta = it.get("meta", {})
            body = ""
            if budget > 0:
                body = _full_page_text(it["url"])
                if body:
                    budget -= 1
            body = body or meta.get("abstract") or meta.get("desc") or ""
            blob.append(f"[{it['source']}] {it['title']}\n{body}\n{it['url']}")
    resp = complete([{"role": "user", "content": f"Summarize all this into a daily digest:\n\n{chr(10).join(blob)}"}], max_tokens=2000)
    print(f"\n🔬 naive — main input_tokens={resp.usage.input_tokens}")
    return text_of(resp)

def main():
    naive = "--naive" in sys.argv
    title = CFG["delivery"]["title"]
    if naive:
        run_naive()
        print("(comparison only, not delivered)")
        return
    body = run_correct()
    channel = CFG["delivery"]["channel"]
    r = deliver.deliver(channel, title, body)
    print(f"\n📤 deliver({channel}): {r}")
    digest.append(title, body)
    print("📝 digest.md updated")

if __name__ == "__main__":
    main()
