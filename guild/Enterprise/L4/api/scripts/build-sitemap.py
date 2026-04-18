#!/usr/bin/env python3
# @tag-event
# {
#   "id": "build-sitemap:on-paths-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag":  "paths.graph.rebuilt_at",
#     "from": "*",
#     "to":   "CHANGED"
#   },
#   "writes": ["sitemap.xml.rebuilt_at"]
# }
# @end-tag-event
"""
Build /sitemap.xml at repo root from Path UDT instances.

Spec: https://www.sitemaps.org/protocol.html — a <urlset> of <url> entries.
Each entry: <loc>, <lastmod>, <changefreq>, <priority>.

Policy:
  - Public routes only (skip operator dashboard, apps/p2p, internals)
  - Static routes AND dynamic routes (with one entry per resolved slug)
  - robots.txt written at repo root pointing to this sitemap
"""
import json, sys
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "guild" / "Enterprise" / "L2" / "lib"))
from packml import Process, path_exists, has_files

SITE = "https://aicraftspeopleguild.github.io"
PATHS_DIR = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances" / "paths"
PAPER_INSTANCES  = REPO / "guild" / "Enterprise" / "L4" / "api" / "white-papers" / "udts" / "instances"
MEMBER_INSTANCES = REPO / "guild" / "Enterprise" / "L4" / "members" / "udts" / "instances"

PUBLIC_SECTIONS = {"about", "resources", "community", "recognition", "meta"}
EXCLUDE_IDS = {"chief-ai-skeptic", "hushbell-full-spec", "submit"}

def iso_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def load_paths():
    out = []
    for f in sorted(PATHS_DIR.glob("*.json")):
        if f.name.startswith("_"): continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            if d.get("udtType") == "Path":
                out.append(d)
        except Exception:
            pass
    return out

def url_entry(loc, lastmod=None, changefreq="weekly", priority="0.5"):
    return (
        "  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod or iso_now()}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        "  </url>"
    )

def main():
    entries = []
    lastmod = iso_now()

    # Home + operator dashboard
    entries.append(url_entry(f"{SITE}/",           lastmod, "daily",  "1.0"))
    entries.append(url_entry(f"{SITE}/guild/",     lastmod, "weekly", "0.7"))

    # Path UDT-defined routes (public only)
    for p in load_paths():
        params = p.get("parameters", {})
        pid    = p.get("tags", {}).get("id", "")
        if params.get("status") != "published":      continue
        if params.get("section") not in PUBLIC_SECTIONS: continue
        if pid in EXCLUDE_IDS:                       continue

        path = params.get("path", "")
        # Dynamic routes: expand via referenced data source
        if params.get("dynamic"):
            if pid == "white-paper-article" or pid == "app-" in pid:
                for f in sorted(PAPER_INSTANCES.glob("*.json")):
                    slug = f.stem
                    loc  = f"{SITE}/#/whitepapers/{slug}"
                    entries.append(url_entry(loc, lastmod, "monthly", "0.7"))
            elif pid == "member-profile":
                for f in sorted(MEMBER_INSTANCES.glob("*.json")):
                    slug = f.stem
                    loc  = f"{SITE}/#/members/{slug}"
                    entries.append(url_entry(loc, lastmod, "monthly", "0.6"))
            continue

        # Static route — emit as hash route (what the SPA uses)
        loc = f"{SITE}/#{path}" if path.startswith("/") else f"{SITE}/{path}"
        priority = "0.8" if pid in ("manifesto", "white-papers", "charter") else "0.6"
        entries.append(url_entry(loc, lastmod, "weekly", priority))

    # Static API endpoints (machine consumers)
    for api in ["Enterprise/L4/api/papers.json", "Enterprise/L4/api/members.json", "Enterprise/L4/api/health.json"]:
        entries.append(url_entry(f"{SITE}/guild/{api}", lastmod, "daily", "0.4"))

    # Apps
    for app in ["whitepapers", "p2p"]:
        entries.append(url_entry(f"{SITE}/guild/apps/{app}/", lastmod, "weekly", "0.5"))

    body = "\n".join(entries)
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body + "\n"
        "</urlset>\n"
    )
    (REPO / "sitemap.xml").write_text(xml, encoding="utf-8")

    # robots.txt — points to the sitemap + invites crawlers
    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE}/sitemap.xml\n"
    )
    (REPO / "robots.txt").write_text(robots, encoding="utf-8")

    print(f"[sitemap] wrote sitemap.xml ({len(entries)} URLs) + robots.txt")

if __name__ == "__main__":
    with Process(
        "api--build-sitemap_py",
        pre_checks=[has_files(PATHS_DIR / "*.json", min_count=10)],
        post_checks=[path_exists(REPO / "sitemap.xml"), path_exists(REPO / "robots.txt")],
    ):
        main()
