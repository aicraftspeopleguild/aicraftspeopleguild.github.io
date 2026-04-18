#!/usr/bin/env python3
"""
One-shot fixer for stale links in views/data/*.data.json and apps/data.

Rewrites:
  - href="aicraftspeopleguild-manifesto.html" -> href="manifesto.html"
  - href="chief-ai-skeptic-officer.html"      -> href="chief-ai-skeptic.html"
  - href="../index.html#X"                    -> href="../../../index.html#X"
  - href="../../../index.html"                -> kept (already correct from dist/)
  - href="../white-papers/X.html"             -> href="app-X.html" (app pages)

Idempotent — re-running has no effect once links are fixed.
"""
import json, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

VIEW_DATA = REPO / "guild" / "web" / "views" / "data"
APP_DATA  = REPO / "guild" / "apps" / "whitepapers" / "data"

# (pattern, replacement) — order matters
REPLACEMENTS = [
    # Manifesto rename: long slug -> short
    (re.compile(r'((?:href|src)\s*=\s*["\'])aicraftspeopleguild-manifesto\.html(["\'])'),
     r'\1manifesto.html\2'),
    # Chief AI Skeptic Officer rename
    (re.compile(r'((?:href|src)\s*=\s*["\'])chief-ai-skeptic-officer\.html(["\'])'),
     r'\1chief-ai-skeptic.html\2'),
    # ../index.html#X (was correct from static/, now wrong from dist/)
    # dist/X.html needs ../../../index.html to reach repo-root index.html
    (re.compile(r'((?:href)\s*=\s*["\'])\.\./index\.html(#[a-zA-Z0-9_-]+)?(["\'])'),
     r'\1../../../index.html\2\3'),
    # ../../../web/X.html  -> X.html (since both are in dist/ now)
    (re.compile(r'((?:href|src)\s*=\s*["\'])\.\./(?:\.\./)?web/dist/([\w-]+\.html)(["\'])'),
     r'\1\2\3'),
    # White paper paths in apps: ../white-papers/foo.html -> #/whitepapers/foo
    (re.compile(r'((?:href)\s*=\s*["\'])\.\./white-papers/([a-z][\w-]*?)\.html(["\'])'),
     r'\1#/whitepapers/\2\3'),
    # Absolute prod URLs to deleted paper files -> hash routes
    (re.compile(r'((?:href)\s*=\s*["\'])https://aicraftspeopleguild\.github\.io/guild/web/white-papers/([\w-]+)\.html(["\'])'),
     r'\1#/whitepapers/\2\3'),
]

def fix_html(html):
    for pat, repl in REPLACEMENTS:
        html = pat.sub(repl, html)
    return html

def fix_dir(d, body_keys):
    if not d.exists():
        return 0
    n = 0
    for f in sorted(d.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        changed = False
        for k in body_keys:
            v = data.get(k)
            if isinstance(v, str):
                new = fix_html(v)
                if new != v:
                    data[k] = new
                    changed = True
        if changed:
            f.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            n += 1
    return n

def main():
    page_count = fix_dir(VIEW_DATA, ["body"])
    app_count  = fix_dir(APP_DATA, ["body_html"])
    print(f"[fix-data-links] updated {page_count} view data files")
    print(f"[fix-data-links] updated {app_count} app data files")

if __name__ == "__main__":
    main()
