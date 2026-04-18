"""Shared helpers for the ACG build pipeline.

Import-time side effects: none. Each submodule is independently importable.

Modules:
  slugify         - slugify(), safe_slug()
  yaml_front      - yaml_value(), frontmatter()
  html_to_md      - parse(), clean_body(), to_markdown()
  md_to_html      - render()
  link_rewrite    - for_spa(), for_paper_app()
  packml_states   - IDLE, STARTING, EXECUTE, COMPLETING, COMPLETE, ABORTED...
  packml_checks   - CheckFailed, path_exists(), has_files()
  packml_process  - Process context manager

Legacy: lib/packml.py re-exports Process + helpers for existing callers.
"""
