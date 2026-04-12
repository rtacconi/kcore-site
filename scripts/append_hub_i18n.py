#!/usr/bin/env python3
"""Append docs hub/sidebar keys after userdoc.manifests.vm.storagesize.type in each language block."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "scripts" / "doc-hub-translations.cache.json"
I18N = ROOT / "js" / "i18n.js"

MARKER = '    "userdoc.manifests.vm.storagesize.type":'


def js_escape(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)[1:-1]


def main() -> int:
    cache = json.loads(CACHE.read_text(encoding="utf-8"))
    lines = I18N.read_text(encoding="utf-8").splitlines(keepends=True)

    idxs = [i for i, ln in enumerate(lines) if ln.startswith(MARKER)]
    if len(idxs) != 8:
        print(f"Expected 8 {MARKER} lines, got {len(idxs)}", file=sys.stderr)
        return 1

    langs = ["en", "it", "es", "fr", "de", "pt", "ja", "zh"]
    for bi in range(7, -1, -1):
        idx = idxs[bi]
        lang = langs[bi]
        trans = cache[lang]
        extra_lines = []
        for k in sorted(trans.keys()):
            extra_lines.append(f'    "{js_escape(k)}": "{js_escape(trans[k])}",\n')
        # Last userdoc line already has comma from merge; manifests line should end with comma
        line = lines[idx]
        if not line.rstrip().endswith(","):
            lines[idx] = line.rstrip() + ",\n"
        lines.insert(idx + 1, "".join(extra_lines))

    I18N.write_text("".join(lines), encoding="utf-8")
    print("Appended hub keys to", I18N)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
