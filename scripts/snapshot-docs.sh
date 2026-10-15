#!/usr/bin/env bash
# Freeze docs/user as docs/<version>/user and point /docs/user at that version.
# Usage: ./scripts/snapshot-docs.sh X.Y.Z <schemaVersion>
set -euo pipefail

ROOT="$(cd "$(dirname "${0}")/.." && pwd)"
cd "${ROOT}"

VERSION="${1:-}"
SCHEMA="${2:-}"
[[ "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
	echo "usage: $0 X.Y.Z <schemaVersion>" >&2
	exit 1
}
[[ "${SCHEMA}" =~ ^[0-9]+$ ]] || {
	echo "schemaVersion must be an integer (SCHEMA_VERSION in kcore crates/controller/src/db.rs)" >&2
	exit 1
}

ISO="kcoreos-${VERSION}-x86_64-linux.iso"
python3 - "${VERSION}" "${SCHEMA}" "${ISO}" <<'PY'
import json, pathlib, sys
version, schema, iso = sys.argv[1], int(sys.argv[2]), sys.argv[3]
root = pathlib.Path("docs")
versions_path = root / "versions.json"
doc = {"latest": version, "versions": []}
if versions_path.exists():
    doc = json.loads(versions_path.read_text())
versions = [v for v in doc.get("versions", []) if v.get("version") != version]
entry = {
    "version": version,
    "schemaVersion": schema,
    "iso": iso,
    "docsUrl": f"https://kcorehypervisor.com/docs/{version}/",
}
versions.insert(0, entry)
versions.sort(key=lambda v: [int(p) for p in v["version"].split(".")], reverse=True)
doc = {"latest": version, "versions": versions}
versions_path.write_text(json.dumps(doc, indent=2) + "\n")
print(f"wrote {versions_path}")
PY

DEST="docs/${VERSION}/user"
rm -rf "${DEST}"
mkdir -p "${DEST}"
cp -a docs/user/. "${DEST}/"

python3 - "${VERSION}" <<'PY'
import pathlib, sys
version = sys.argv[1]
banner = (
    f'<p class="docs-version-banner" data-docs-version="{version}"></p>\n            '
)
script = '<script src="../../../js/docs-version.js"></script>'
for path in pathlib.Path(f"docs/{version}/user").glob("*.html"):
    text = path.read_text()
    text = text.replace('href="../../css/', 'href="../../../css/')
    text = text.replace('href="../../js/', 'href="../../../js/')
    text = text.replace('src="../../js/', 'src="../../../js/')
    text = text.replace("https://kcorehypervisor.com/docs/user/", f"https://kcorehypervisor.com/docs/{version}/user/")
    text = text.replace('src="../../../js/docs-version.js"', 'src="../../../js/docs-version.js"')
    if 'class="docs-version-banner"' not in text:
        text = text.replace('<main class="docs-content">', '<main class="docs-content">\n            ' + banner, 1)
    else:
        text = text.replace('data-docs-version="latest"', f'data-docs-version="{version}"')
    if "docs-version.js" not in text:
        text = text.replace("</body>", f"    {script}\n</body>")
    else:
        text = text.replace('src="../../js/docs-version.js"', 'src="../../../js/docs-version.js"')
    path.write_text(text)
    print(f"froze {path}")
PY

python3 - <<'PY'
import pathlib
banner = '<p class="docs-version-banner" data-docs-version="latest"></p>\n            '
script = '<script src="../../js/docs-version.js"></script>'
for path in pathlib.Path("docs/user").glob("*.html"):
    text = path.read_text()
    if 'class="docs-version-banner"' not in text:
        text = text.replace('<main class="docs-content">', '<main class="docs-content">\n            ' + banner, 1)
    if "docs-version.js" not in text:
        text = text.replace("</body>", f"    {script}\n</body>")
    path.write_text(text)
print("latest docs/user pages carry the version switcher")
PY
