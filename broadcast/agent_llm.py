import os
from anthropic import Anthropic

_client = None

def client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(
            api_key=os.environ.get("PARALLIGHT_API_KEY", ""),
            base_url=os.environ.get("PARALLIGHT_BASE_URL", "https://token.parallight.ai/api/llm"),
        )
    return _client

MODEL = os.environ.get("PARALLIGHT_MODEL", "claude-sonnet-4-6")

def complete(messages, tools=None, system=None, max_tokens=1024):
    kwargs = {"model": MODEL, "max_tokens": max_tokens, "messages": messages}
    if tools:
        kwargs["tools"] = tools
    if system:
        kwargs["system"] = system
    return client().messages.create(**kwargs)

def text_of(resp) -> str:
    return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip()
