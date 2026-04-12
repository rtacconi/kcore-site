#!/usr/bin/env python3
"""Merge doc-i18n-translations.cache.json into js/i18n.js after each bp.sg.outro line."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "scripts" / "doc-i18n-translations.cache.json"
I18N = ROOT / "js" / "i18n.js"

LANG_ORDER = ["en", "it", "es", "fr", "de", "pt", "ja", "zh"]


def js_escape(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)[1:-1]


def format_block(trans: dict[str, str]) -> str:
    lines = []
    for k in sorted(trans.keys()):
        lines.append(f'    "{js_escape(k)}": "{js_escape(trans[k])}",')
    return "\n".join(lines) + "\n"


def main() -> int:
    if not CACHE.exists():
        print("Missing cache; run translate_doc_i18n.py first", file=sys.stderr)
        return 1
    cache = json.loads(CACHE.read_text(encoding="utf-8"))

    for lang in LANG_ORDER:
        if lang not in cache or not cache[lang]:
            print(f"Missing cache['{lang}']", file=sys.stderr)
            return 1

    lines = I18N.read_text(encoding="utf-8").splitlines(keepends=True)

    outro_idxs = [i for i, ln in enumerate(lines) if '"bp.sg.outro"' in ln and "expose-nginx-host.yaml" in ln]
    if len(outro_idxs) != 8:
        print(f"Expected 8 bp.sg.outro lines, found {len(outro_idxs)}", file=sys.stderr)
        return 1

    # Insert from bottom to top so line indices stay valid
    for block_i in range(7, -1, -1):
        idx = outro_idxs[block_i]
        lang = LANG_ORDER[block_i]
        line = lines[idx]
        if not line.rstrip().endswith(","):
            lines[idx] = line.rstrip() + ",\n"
        extra = format_block(cache[lang])
        lines.insert(idx + 1, extra)

    I18N.write_text("".join(lines), encoding="utf-8")
    print("Merged doc i18n into", I18N)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
