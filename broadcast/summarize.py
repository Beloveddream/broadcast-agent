from .agent_llm import complete, text_of

def summarize_source(source_name, items, keywords, max_tokens):
    if not items:
        return {"source": source_name, "summary": "_(no items today)_", "usage": _zero()}
    lines = []
    for it in items:
        meta = it.get("meta", {})
        extra = meta.get("abstract") or meta.get("desc") or ""
        tag = f"({meta['points']}pts)" if meta.get("points") is not None else (f"(+{meta['stars_today']})" if meta.get("stars_today") else "")
        lines.append(f"- {it['title']} {tag}\n  {extra[:300]}\n  {it['url']}")
    blob = "\n".join(lines)
    system = (f"You are a summarizer sub-agent. Pick 3-6 items most relevant to: {', '.join(keywords)}. "
              "One sentence per item explaining what it is and why it matters, with link. Markdown list only.")
    resp = complete([{"role": "user", "content": f"# {source_name}\n{blob}"}], system=system, max_tokens=max_tokens)
    return {"source": source_name, "summary": text_of(resp), "usage": resp.usage}

class _zero:
    input_tokens = 0
    output_tokens = 0
