#!/usr/bin/env python3
"""Vérifie title, H1, meta description inchangés vs main (même chemins HTML)."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_GLOBS = list(ROOT.glob("**/index.html"))

FIELDS = ("title", "h1", "meta_description")


def extract(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    title_m = re.search(r"<title>([^<]*)</title>", text)
    meta_m = re.search(
        r'<meta\s+name="description"\s+content="([^"]*)"',
        text,
        re.I,
    )
    h1_m = re.search(r'<h1[^>]*id="(?:page-h1|hero-h1)"[^>]*>([^<]*)</h1>', text)
    if not h1_m:
        h1_m = re.search(r"<h1[^>]*>([^<]*)</h1>", text)
    return {
        "title": title_m.group(1) if title_m else None,
        "meta_description": meta_m.group(1) if meta_m else None,
        "h1": h1_m.group(1) if h1_m else None,
    }


def main():
    changed = []
    for path in sorted(HTML_GLOBS):
        rel = path.relative_to(ROOT).as_posix()
        try:
            old = subprocess.check_output(
                ["git", "show", f"main:{rel}"],
                cwd=ROOT,
                text=True,
            )
        except subprocess.CalledProcessError:
            continue
        old_path = Path("/tmp") / rel.replace("/", "__")
        old_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.write_text(old, encoding="utf-8")
        cur = extract(path)
        prev = extract(old_path)
        for key in FIELDS:
            if cur.get(key) != prev.get(key):
                changed.append((rel, key, prev.get(key), cur.get(key)))
    out = Path("/opt/cursor/artifacts/seo-verify.json")
    out.write_text(
        __import__("json").dumps({"changes": changed, "count": len(changed)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if changed:
        for row in changed[:30]:
            print("CHANGED", row)
        raise SystemExit(len(changed))
    print("SEO spot-check OK (title, meta, h1)")


if __name__ == "__main__":
    main()
