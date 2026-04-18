#!/usr/bin/env python3
# @tag-event
# {
#   "id": "apps-build-whitepapers:on-papers-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "papers.count",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "apps.whitepapers.rebuilt_at"
#   ]
# }
# @end-tag-event
"""
Generate one App per white paper UDT instance.

For each guild/Enterprise/L4/api/white-papers/udts/instances/<slug>.json:
  - Render the markdown body to HTML
  - Write guild/apps/whitepapers/udts/instances/<slug>.json (App instance)
  - Write guild/apps/whitepapers/data/<slug>.data.json (paper data + body_html)
  - Write guild/apps/whitepapers/pages/<slug>.page.json (route + view binding)
  - Add a Path UDT instance to guild/Enterprise/L2/hmi/web/components/udts/instances/paths/

The build step (build.js) then renders each app to dist/apps/<slug>.html.
"""
import json, sys
from pathlib import Path
from datetime import datetime, timezone
import markdown

# PackML wrapper (scripts/lib/packml.py)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from packml import Process, path_exists, has_files

REPO = Path(__file__).resolve().parents[4]
WP_INSTANCES = REPO / "guild" / "Enterprise" / "L4" / "api" / "white-papers" / "udts" / "instances"
APP_DIR = REPO / "guild" / "apps" / "whitepapers"
APP_TEMPLATE = APP_DIR / "udts" / "templates" / "app.udt.json"
PATHS_DIR = REPO / "guild" / "Enterprise" / "L2" / "hmi" / "web" / "components" / "udts" / "instances" / "paths"

TYPE_LABEL = {
    "published":           "White Paper",
    "position":            "Position Paper",
    "experimental":        "Experimental",
    "research-note":       "Research Note",
    "knowledge-about-knowledge": "Knowledge About Knowledge",
    "draft":               "Draft White Paper",
}

def load_template_version():
    if APP_TEMPLATE.exists():
        return json.loads(APP_TEMPLATE.read_text(encoding="utf-8")).get("version", "1.0.0")
    return "1.0.0"

def render_markdown(md_text):
    if not md_text:
        return ""
    html = markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables", "attr_list", "toc"]
    )
    return rewrite_paper_links(html)

# White paper bodies were extracted when papers lived as siblings to their
# images (e.g., href="fratally-wrong.jpeg"). The rendered apps now live in
# guild/web/dist/, so image refs need an explicit root-absolute prefix.
import re as _re
PAPER_IMAGE_PATTERN = _re.compile(
    r'((?:href|src)\s*=\s*["\'])(?!https?://|#|/|\.\./|data:|mailto:)([\w\-]+\.(?:png|jpe?g|gif|svg|webp|mp4|pdf))(["\'])',
    _re.IGNORECASE
)
def rewrite_paper_links(html):
    """Rewrite links inside paper body to work from guild/web/dist/app-X.html."""
    # 1. Bare image refs -> /guild/Enterprise/L4/api/white-papers/<img>
    html = PAPER_IMAGE_PATTERN.sub(
        lambda m: m.group(1) + '/guild/Enterprise/L4/api/white-papers/' + m.group(2) + m.group(3),
        html
    )
    # 2. Absolute prod URLs to deleted paper HTML files -> hash routes
    html = _re.sub(
        r'(href\s*=\s*["\'])https?://aicraftspeopleguild\.github\.io/guild/(?:web|Enterprise/L4/api)/white-papers/([a-z][\w-]*?)\.html(["\'])',
        lambda m: m.group(1) + '#/whitepapers/' + m.group(2) + m.group(3),
        html
    )
    # 3. Relative paper HTML refs (e.g., ../white-papers/foo.html) -> hash route
    html = _re.sub(
        r'(href\s*=\s*["\'])(?:\.\./)?white-papers/([a-z][\w-]*?)\.html(["\'])',
        lambda m: m.group(1) + '#/whitepapers/' + m.group(2) + m.group(3),
        html
    )
    # 4. Sibling .html refs from inter-paper markdown links -> hash route
    html = _re.sub(
        r'(href\s*=\s*["\'])(?!https?://|#|/|\.\.?/|mailto:)([a-z][\w-]*?)\.html(["\'])',
        lambda m: m.group(1) + '#/whitepapers/' + m.group(2) + m.group(3),
        html
    )
    return html

def safe_slug(slug, max_len=60):
    """Truncate overly long slugs at word boundaries to stay under Windows MAX_PATH."""
    if len(slug) <= max_len:
        return slug
    # Trim to max_len at the last hyphen boundary
    truncated = slug[:max_len]
    last_hyphen = truncated.rfind("-")
    if last_hyphen > max_len // 2:
        truncated = truncated[:last_hyphen]
    return truncated

def main():
    if not WP_INSTANCES.exists():
        print(f"[error] not found: {WP_INSTANCES}")
        return

    schema = load_template_version()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    instances = sorted(WP_INSTANCES.glob("*.json"))
    print(f"[apps] generating {len(instances)} white paper apps")

    # Ensure paths dir exists (defensive — may be a fresh checkout)
    PATHS_DIR.mkdir(parents=True, exist_ok=True)

    for inst_path in instances:
        wp = json.loads(inst_path.read_text(encoding="utf-8"))
        params = wp.get("parameters", {})
        tags   = wp.get("tags", {})
        full_slug = tags.get("id") or inst_path.stem
        slug = safe_slug(full_slug)

        # 1. Data: paper metadata + body_html
        body_md = tags.get("body", "")
        body_html = render_markdown(body_md)
        data = {
            "title":      params.get("title") or slug,
            "subtitle":   params.get("doc_number") or "",
            "summary":    params.get("summary") or "",
            "authors":    params.get("authors") or [],
            "date":       params.get("publication_date") or "",
            "doc_number": params.get("doc_number") or "",
            "tags":       params.get("tags") or [],
            "status":     params.get("status") or "published",
            "type_label": TYPE_LABEL.get(params.get("status") or "published", "White Paper"),
            "body_html":  body_html,
        }
        (APP_DIR / "data" / f"{slug}.data.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # 2. App UDT instance
        app = {
            "udtType": "App",
            "parameters": {
                "name":        params.get("title") or slug,
                "slug":        slug,
                "kind":        "white-paper",
                "description": params.get("summary") or "",
                "source_type": "WhitePaper",
                "source_path": f"guild/Enterprise/L4/api/white-papers/udts/instances/{inst_path.name}",
                "view":        "guild/apps/whitepapers/views/white-paper-app.view.json",
                "data":        {"paper": f"guild/apps/whitepapers/data/{slug}.data.json"},
                "route":       f"/whitepapers/{slug}",
                "section":     "resources",
                "stylesheets": ["guild/Enterprise/L2/hmi/web/style/main.css"],
                "status":      "published",
                "tags":        params.get("tags") or []
            },
            "tags": {
                "id":             slug,
                "url":            f"https://aicraftspeopleguild.github.io/guild/apps/whitepapers/{slug}/",
                "view_id":        "white-paper-app",
                "ingested_at":    now,
                "schema_version": schema
            }
        }
        (APP_DIR / "udts" / "instances" / f"{slug}.json").write_text(
            json.dumps(app, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # 3. Page UDT (so build.js renders this app)
        page = {
            "udtType": "Page",
            "parameters": {
                "title":       params.get("title") or slug,
                "slug":        f"app-{slug}",
                "route":       f"/whitepapers/{slug}",
                "view":        "guild/apps/whitepapers/views/white-paper-app.view.json",
                "data":        {"paper": f"guild/apps/whitepapers/data/{slug}.data.json"},
                "stylesheets": ["guild/Enterprise/L2/hmi/web/style/main.css"],
                "section":     "resources",
                "parent_slug": "white-papers",
                "status":      "published"
            },
            "tags": {
                "id": f"app-{slug}",
                "view_id": "white-paper-app",
                "schema_version": "1.0.0"
            }
        }
        (APP_DIR / "pages" / f"{slug}.page.json").write_text(
            json.dumps(page, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # 4. Path UDT instance — register the route
        path_inst = {
            "udtType": "Path",
            "parameters": {
                "path":           f"/whitepapers/{slug}",
                "label":          params.get("title") or slug,
                "page":           f"guild/apps/whitepapers/pages/{slug}.page.json",
                "section":        "resources",
                "parent":         "white-papers",
                "order":          100,
                "dynamic":        False,
                "params":         [],
                "methods":        ["GET"],
                "status":         "published",
                "visible_in_nav": False,
                "access":         "public"
            },
            "tags": {
                "id":             f"app-{slug}",
                "full_url":       f"https://aicraftspeopleguild.github.io/whitepapers/{slug}",
                "children":       [],
                "breadcrumb":     ["home", "white-papers", f"app-{slug}"],
                "depth":          2,
                "view_id":        "white-paper-app",
                "last_verified":  now,
                "schema_version": "1.0.0"
            }
        }
        (PATHS_DIR / f"app-{slug}.json").write_text(
            json.dumps(path_inst, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # Manifest of all apps
    manifest = {
        "version": "1.0.0",
        "generated_at": now,
        "schema_version": schema,
        "kind": "white-paper",
        "count": len(instances),
        "apps": sorted([p.stem for p in instances])
    }
    (APP_DIR / "index.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"[apps] {len(instances)} apps:")
    print(f"  udts/instances/  ({len(instances)} App UDT instances)")
    print(f"  data/            ({len(instances)} data files w/ HTML body)")
    print(f"  pages/           ({len(instances)} page bindings)")
    print(f"  paths/           ({len(instances)} Path UDT instances)")
    print(f"  index.json       (manifest)")

if __name__ == "__main__":
    with Process(
        "apps--build-whitepaper-apps_py",
        pre_checks=[
            path_exists(WP_INSTANCES),
            has_files(WP_INSTANCES / "*.json", min_count=10),
            path_exists(APP_TEMPLATE),
        ],
        post_checks=[
            has_files(APP_DIR / "udts" / "instances" / "*.json", min_count=10),
            has_files(APP_DIR / "data" / "*.json", min_count=10),
            has_files(APP_DIR / "pages" / "*.json", min_count=10),
            path_exists(APP_DIR / "index.json"),
        ],
    ):
        main()
