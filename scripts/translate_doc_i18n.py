#!/usr/bin/env python3
"""Translate doc i18n keys via MyMemory API (free tier, max 500 chars per request)."""
from __future__ import annotations

import json
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYS_FILE = ROOT / "scripts" / "doc-i18n-keys.txt"
CACHE_FILE = ROOT / "scripts" / "doc-i18n-translations.cache.json"

LANG_PAIRS = {
    "it": "en|it",
    "es": "en|es",
    "fr": "en|fr",
    "de": "en|de",
    "pt": "en|pt",
    "ja": "en|ja",
    "zh": "en|zh-CN",
}


def load_keys() -> dict[str, str]:
    keys: dict[str, str] = {}
    text = KEYS_FILE.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("userdoc.") or " = " not in line:
            continue
        k, v = line.split(" = ", 1)
        keys[k] = v
    return keys


def translate_mymemory(text: str, langpair: str, retries: int = 3) -> str | None:
    if len(text) > 480:
        text = text[:480]
    url = (
        "https://api.mymemory.translated.net/get?"
        + urllib.parse.urlencode({"q": text, "langpair": langpair})
    )
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "kcore-site-i18n/1.0"})
            with urllib.request.urlopen(req, timeout=12) as r:
                data = json.loads(r.read().decode("utf-8"))
            status = data.get("responseStatus")
            out = data.get("responseData", {}).get("translatedText", "")
            if status == 200 and out and "QUERY LENGTH LIMIT" not in str(out):
                return out
            if "QUERY LENGTH LIMIT" in str(out):
                return None
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            time.sleep(0.4 * (attempt + 1))
    return None


def main() -> int:
    socket.setdefaulttimeout(15)
    keys = load_keys()
    if not keys:
        print("No keys found", file=sys.stderr)
        return 1

    cache: dict[str, dict[str, str]] = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cache = {}

    cache.setdefault("en", {})
    for k, v in keys.items():
        cache["en"][k] = v

    total_calls = len(keys) * len(LANG_PAIRS)
    n_done = 0

    for lang, pair in LANG_PAIRS.items():
        cache.setdefault(lang, {})
        for k, v in keys.items():
            if k in cache[lang] and cache[lang][k]:
                n_done += 1
                continue
            t = translate_mymemory(v, pair)
            cache[lang][k] = t if t is not None else v
            n_done += 1
            CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
            if n_done % 50 == 0:
                print(f"{n_done}/{total_calls}", flush=True)
            time.sleep(0.08)

    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {CACHE_FILE} ({len(cache)} langs)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
