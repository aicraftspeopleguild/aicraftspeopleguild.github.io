#!/usr/bin/env python3
# @tag-event
# {
#   "id": "test-links:on-build-complete",
#   "listens": {
#     "kind": "on_transition",
#     "tag":  "pipeline.build.status",
#     "from": "RUNNING",
#     "to":   "COMPLETE"
#   },
#   "reads":  ["guild.web.dist.*"],
#   "writes": ["qa.links.ok", "qa.links.missing_count"]
# }
# @end-tag-event
"""
Test internal href/src links across index.html + all built dist/ pages.

For each HTML file:
  - Parse every href and src attribute
  - Skip externals (http:, https:, mailto:, javascript:) and pure fragments (#foo)
  - Resolve hash routes (#/charter) against site-map.json
  - Resolve relative paths against the file's directory
  - Verify the target file exists

Reports per-file broken-link counts and a summary.
"""
import re, sys, json
from pathlib import Path
from urllib.parse import urlparse, unquote

REPO = Path(__file__).resolve().parents[3]

HREF_RE = re.compile(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)

def is_external(url):
    if url.startswith(("http://", "https://", "mailto:", "javascript:", "data:")):
        return True
    if url.startswith("//"):
        return True
    return False

def is_pure_fragment(url):
    return url.startswith("#") and not url.startswith("#/")

def load_site_map():
    smfile = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "site-map.json"
    if not smfile.exists():
        return None
    return json.loads(smfile.read_text(encoding="utf-8"))

def load_paths():
    paths_dir = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances" / "paths"
    paths = {}
    if not paths_dir.exists():
        return paths
    for f in paths_dir.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        p = d.get("parameters", {})
        if p.get("path"):
            paths[p["path"]] = d
    return paths

def resolve_hash_route(url, paths):
    """Hash route #/foo -> check if /foo exists in Path UDT registry."""
    route = url[1:]  # strip leading #
    if not route.startswith("/"):
        return None  # plain anchor
    if route in paths:
        return ("ROUTE_OK", route)
    # Try matching dynamic routes (:slug)
    for p, inst in paths.items():
        if not inst.get("parameters", {}).get("dynamic"):
            continue
        pattern = re.escape(p).replace(r"\:slug", r"[^/]+")
        if re.fullmatch(pattern, route):
            return ("ROUTE_OK", route)
    return ("ROUTE_MISSING", route)

def check_link(html_file, url, site_map, paths):
    """Return (status, detail) where status is OK | MISSING | EXTERNAL | SKIP."""
    if is_external(url):
        return ("EXTERNAL", url)
    if is_pure_fragment(url):
        return ("SKIP", "anchor only")

    if url.startswith("#/"):
        result = resolve_hash_route(url, paths)
        if not result:
            return ("SKIP", "anchor")
        return result

    # Strip query/fragment
    parsed = urlparse(url)
    target = unquote(parsed.path)
    if not target:
        return ("SKIP", "no path")

    # Resolve relative to the html_file's directory
    base = html_file.parent
    if target.startswith("/"):
        # Site-absolute (rare in this repo)
        full = REPO / target.lstrip("/")
    else:
        full = (base / target).resolve()

    # If pointing to a directory, check for index.html
    if full.is_dir():
        full = full / "index.html"

    if full.exists():
        return ("OK", str(full.relative_to(REPO)))
    return ("MISSING", target)

def scan_file(html_file, site_map, paths):
    text = html_file.read_text(encoding="utf-8", errors="replace")
    results = {"OK": 0, "MISSING": [], "EXTERNAL": 0, "SKIP": 0, "ROUTE_OK": 0, "ROUTE_MISSING": []}
    for url in HREF_RE.findall(text):
        status, detail = check_link(html_file, url, site_map, paths)
        if status in ("OK", "ROUTE_OK", "EXTERNAL", "SKIP"):
            results[status] += 1
        else:
            results[status].append((url, detail))
    return results

def main():
    site_map = load_site_map()
    paths = load_paths()

    targets = [REPO / "index.html"]
    dist = REPO / "guild" / "web" / "dist"
    if dist.exists():
        targets += sorted(dist.glob("*.html"))

    print(f"Testing {len(targets)} HTML files")
    print(f"Site map paths registered: {len(paths)}")
    print()

    total_ok = 0
    total_missing = 0
    total_route_missing = 0
    files_with_issues = 0
    issue_detail = []

    for f in targets:
        rel = f.relative_to(REPO)
        r = scan_file(f, site_map, paths)
        ok = r["OK"] + r["ROUTE_OK"]
        miss = len(r["MISSING"])
        route_miss = len(r["ROUTE_MISSING"])
        total_ok += ok
        total_missing += miss
        total_route_missing += route_miss
        if miss or route_miss:
            files_with_issues += 1
            issue_detail.append((rel, r["MISSING"], r["ROUTE_MISSING"]))

    # Print per-file issues
    if issue_detail:
        print("=== Files with broken links ===")
        for rel, miss, route_miss in issue_detail:
            print(f"\n  {rel}:")
            for url, detail in miss:
                print(f"    [MISSING file]   {url}  ->  {detail}")
            for url, detail in route_miss:
                print(f"    [MISSING route]  {url}  ->  {detail}")

    print()
    print(f"=== Summary ===")
    print(f"  Total OK:               {total_ok}")
    print(f"  Total MISSING (file):   {total_missing}")
    print(f"  Total MISSING (route):  {total_route_missing}")
    print(f"  Files with issues:      {files_with_issues} / {len(targets)}")
    if total_missing or total_route_missing:
        sys.exit(1)
    print(f"  [OK] All internal links resolve.")

if __name__ == "__main__":
    main()
