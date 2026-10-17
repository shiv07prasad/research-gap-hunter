"""Thin OpenAI wrapper with an on-disk cache.

The cache means a PDF or embedding that was processed once (e.g. during
rehearsal) works again without network access - the demo safety net.
"""
import hashlib
import json

from openai import OpenAI

from . import config

_client = None


def client() -> OpenAI:
    global _client
    if _client is None:
        if not config.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is missing from .env")
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


def _cache_get(kind: str, key: str):
    path = config.CACHE_DIR / f"{kind}_{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _cache_put(kind: str, key: str, value):
    path = config.CACHE_DIR / f"{kind}_{key}.json"
    path.write_text(json.dumps(value), encoding="utf-8")


def _hash(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:24]


def chat_json(system: str, user: str, cache: bool = True, cache_key: str | None = None,
              model: str | None = None) -> dict:
    """Ask the chat model for a JSON object.

    `cache_key` pins the cache entry to something stable (e.g. system prompt + PDF text) so
    the same document always gives the same extraction, even if the graph vocabulary changed.
    """
    model = model or config.OPENAI_CHAT_MODEL
    key = _hash(model, cache_key) if cache_key else _hash(model, system, user)
    if cache and (hit := _cache_get("chat", key)) is not None:
        return hit
    resp = client().chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    result = json.loads(resp.choices[0].message.content)
    if cache:
        _cache_put("chat", key, result)
    return result


def embed(text: str) -> list[float]:
    key = _hash(config.OPENAI_EMBED_MODEL, text)
    if (hit := _cache_get("embed", key)) is not None:
        return hit
    resp = client().embeddings.create(model=config.OPENAI_EMBED_MODEL, input=text)
    vector = resp.data[0].embedding
    _cache_put("embed", key, vector)
    return vector
