#!/usr/bin/env python3
# @tag-event
# {
#   "id": "members-extract:on-members-changed",
#   "listens": {
#     "kind": "on_transition",
#     "tag": "members.source.changed",
#     "from": "*",
#     "to": "CHANGED"
#   },
#   "writes": [
#     "members.extracted.at",
#     "members.count"
#   ]
# }
# @end-tag-event
"""
Extract member profiles from HTML into markdown originals + Member UDT instances.

For each guild/web/members/<slug>/index.html:
  - Parse name, role/title, bio, expertise tags, avatar filename
  - Write guild/web/members/originals/<slug>.md with YAML front-matter
  - Write guild/web/members/udts/instances/<slug>.json
"""
import re, json, sys
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from markdownify import markdownify as md

REPO = Path(__file__).resolve().parents[4]
MEMBERS_DIR = REPO / "guild" / "Enterprise" / "L4" / "members"
ORIG_DIR = MEMBERS_DIR / "originals"
INST_DIR = MEMBERS_DIR / "udts" / "instances"
TEMPLATE = MEMBERS_DIR / "udts" / "templates" / "member.udt.json"

def load_template_version():
    if TEMPLATE.exists():
        with TEMPLATE.open(encoding="utf-8") as f:
            return json.load(f).get("version", "1.0.0")
    return "1.0.0"

def extract(html_path):
    slug = html_path.parent.name
    text = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(text, "html.parser")

    data = {
        "slug": slug,
        "name": None,
        "title": None,
        "role": None,
        "bio": None,
        "avatar_filename": None,
        "expertise_tags": [],
    }

    # Name from h1 or h2
    h1 = soup.find("h1")
    if h1:
        data["name"] = h1.get_text(strip=True)

    # Title from subtitle or eyebrow
    subtitle = soup.select_one("p.subtitle, .subtitle")
    if subtitle:
        data["title"] = subtitle.get_text(strip=True)

    eyebrow = soup.select_one(".eyebrow")
    if eyebrow:
        data["role"] = eyebrow.get_text(strip=True).lower()

    # Avatar filename from first img src in the profile
    img = soup.select_one(".member-photo img, .profile-photo img, img")
    if img and img.get("src"):
        src = img["src"]
        # Keep just the filename (paths may be relative)
        data["avatar_filename"] = Path(src).name

    # Expertise tags from .member-tags
    for tag_el in soup.select(".member-tags span, .expertise-tags span, .tag"):
        t = tag_el.get_text(strip=True)
        if t and t not in data["expertise_tags"]:
            data["expertise_tags"].append(t)

    # Bio: main content paragraphs from profile-shell or profile-body
    content_root = (
        soup.select_one(".profile-shell, .profile-body, main.container, main")
        or soup.body
    )
    # Remove chrome
    for sel in ["header", "footer", ".back-link", ".cta-section",
                "nav", "script", "style", ".member-photo", "figure"]:
        for el in content_root.select(sel):
            el.decompose()

    bio_md = md(str(content_root), heading_style="ATX", bullets="-")
    bio_md = re.sub(r"\n{3,}", "\n\n", bio_md).strip()
    data["bio"] = bio_md

    return data

def write_markdown(d):
    fm_lines = ["---"]
    fm_lines.append(f'name: "{d["name"]}"' if d["name"] else 'name: ""')
    fm_lines.append(f'slug: {d["slug"]}')
    if d["role"]:
        fm_lines.append(f'role: {d["role"]}')
    if d["title"]:
        fm_lines.append(f'title: "{d["title"]}"')
    if d["avatar_filename"]:
        fm_lines.append(f'avatar_href: {d["avatar_filename"]}')
    if d["expertise_tags"]:
        tags_yaml = "[" + ", ".join(f'"{t}"' for t in d["expertise_tags"]) + "]"
        fm_lines.append(f'expertise_tags: {tags_yaml}')
    fm_lines.append("---\n")
    content = "\n".join(fm_lines) + "\n" + (d["bio"] or "") + "\n"
    out = ORIG_DIR / f"{d['slug']}.md"
    out.write_text(content, encoding="utf-8")
    return out

def write_instance(d, template_version):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    instance = {
        "udtType": "Member",
        "parameters": {
            "name": d["name"] or "",
            "role": d["role"] or "",
            "title": d["title"] or "",
            "bio": d["bio"] or "",
            "avatar_href": d["avatar_filename"] or "",
            "expertise_tags": d["expertise_tags"] or [],
            "links": {},
            "joined_date": "",
        },
        "tags": {
            "id": d["slug"],
            "slug": d["slug"],
            "paper_ids": [],
            "instance_path": f"udts/instances/{d['slug']}.json",
            "ingested_at": now,
            "schema_version": template_version,
        }
    }
    out = INST_DIR / f"{d['slug']}.json"
    out.write_text(json.dumps(instance, indent=2, ensure_ascii=False), encoding="utf-8")
    return out

def main():
    if not MEMBERS_DIR.exists():
        print(f"[error] not found: {MEMBERS_DIR}")
        sys.exit(1)
    ORIG_DIR.mkdir(parents=True, exist_ok=True)
    INST_DIR.mkdir(parents=True, exist_ok=True)

    template_version = load_template_version()

    member_dirs = [d for d in MEMBERS_DIR.iterdir()
                   if d.is_dir() and (d / "index.html").exists()]
    print(f"[extract] found {len(member_dirs)} member pages")

    for md_dir in sorted(member_dirs):
        html = md_dir / "index.html"
        try:
            data = extract(html)
            m_file = write_markdown(data)
            i_file = write_instance(data, template_version)
            print(f"  [write] {data['slug']}: originals/{data['slug']}.md + udts/instances/{data['slug']}.json")
        except Exception as e:
            print(f"  [error] {md_dir.name}: {e}")

    print(f"[extract] done")

if __name__ == "__main__":
    main()
