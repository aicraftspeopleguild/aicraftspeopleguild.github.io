"""
site_base — derive the public GitHub Pages URL of the current repo.

Pages URLs follow two shapes:
  owner.github.io/repo-name     when repo != <owner>.github.io  (project page)
  owner.github.io               when repo == <owner>.github.io  (user/org page)

We figure out which one we're in via the GH_TAG_REPO env var (already
set to `owner/repo` by every workflow that renders SVGs). A SITE_BASE
override wins so local runs can point at any preview host, and if the
env is missing we default to the canonical org site.
"""
import os


def site_base() -> str:
    override = os.environ.get("SITE_BASE", "").rstrip("/")
    if override:
        return override
    repo = os.environ.get("GH_TAG_REPO", "aicraftspeopleguild/aicraftspeopleguild.github.io")
    owner, _, name = repo.partition("/")
    if not name:
        return "https://aicraftspeopleguild.github.io"
    if name == f"{owner}.github.io":
        return f"https://{owner}.github.io"
    return f"https://{owner}.github.io/{name}"
