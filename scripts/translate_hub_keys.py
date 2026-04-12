#!/usr/bin/env python3
"""Translate docs hub/sidebar keys (short batch)."""
import json
import socket
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYS = ROOT / "scripts" / "doc-hub-keys-en.txt"
OUT = ROOT / "scripts" / "doc-hub-translations.cache.json"

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
    d: dict[str, str] = {}
    for line in KEYS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or " = " not in line:
            continue
        k, v = line.split(" = ", 1)
        d[k] = v
    return d


def tr(text: str, pair: str) -> str:
    if len(text) > 480:
        text = text[:480]
    url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode(
        {"q": text, "langpair": pair}
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "kcore-site-i18n/1.0"})
        with urllib.request.urlopen(req, timeout=12) as r:
            data = json.loads(r.read().decode("utf-8"))
        out = data.get("responseData", {}).get("translatedText", "")
        if data.get("responseStatus") == 200 and out and "QUERY LENGTH LIMIT" not in str(out):
            return out
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return text


def main() -> None:
    socket.setdefaulttimeout(15)
    keys = load_keys()
    cache: dict[str, dict[str, str]] = {"en": dict(keys)}
    for lang, pair in LANG_PAIRS.items():
        cache[lang] = {}
        for k, v in keys.items():
            cache[lang][k] = tr(v, pair)
            time.sleep(0.08)
    OUT.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
