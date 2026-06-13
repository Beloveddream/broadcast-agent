from .agent_llm import complete, text_of

def summarize_source(source_name, items, keywords, max_tokens):
    if not items:
        return {"source": source_name, "summary": "_(今日无相关条目)_", "usage": _zero()}
    lines = []
    for it in items:
        meta = it.get("meta", {})
        extra = meta.get("abstract") or meta.get("desc") or ""
        tag = f"({meta['points']}pts)" if meta.get("points") is not None else (f"(+{meta['stars_today']})" if meta.get("stars_today") else "")
        lines.append(f"- {it['title']} {tag}\n  {extra[:300]}\n  {it['url']}")
    blob = "\n".join(lines)
    system = (
        f"你是某个信息源的摘要子 agent。只看下面这一个源的条目，"
        f"挑出和这些关键词最相关的 3-6 条：{', '.join(keywords)}。"
        "每条一句话说清「是什么 + 为什么值得看」，并附上链接。"
        "用中文输出。只输出 markdown 列表，不要寒暄、不要前后缀。"
    )
    resp = complete([{"role": "user", "content": f"# {source_name}\n{blob}"}], system=system, max_tokens=max_tokens)
    return {"source": source_name, "summary": text_of(resp), "usage": resp.usage}

class _zero:
    input_tokens = 0
    output_tokens = 0
