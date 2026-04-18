#!/usr/bin/env python3
"""
Build controls/db/tags.sqlite + controls/db/sql/seed.sql from every
JSON manifest in the project.

Sources:
  controls/scada/gateway/providers/registry.json   · subsystems
  <subsystem>/udts.json                             · UDTs + fields
  <subsystem>/tags.json                             · tag catalog
  controls/scada/programs/**/*.json                 · program manifests

Outputs:
  controls/db/tags.sqlite   · SQLite binary (committed)
  controls/db/sql/seed.sql  · text dump for diff-readable review
"""
from __future__ import annotations
import json, os, sqlite3, sys
from pathlib import Path

ROOT     = Path(__file__).resolve().parent.parent.parent
DB_DIR   = ROOT / 'controls' / 'db'
DB_FILE  = DB_DIR / 'tags.sqlite'
SCHEMA   = DB_DIR / 'sql' / 'schema.sql'
SEED_OUT = DB_DIR / 'sql' / 'seed.sql'
REGISTRY = ROOT / 'controls' / 'scada' / 'gateway' / 'providers' / 'registry.json'


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f'!!  {p} — {e}', file=sys.stderr)
        return None


def fresh_db():
    if DB_FILE.exists():
        DB_FILE.unlink()
    con = sqlite3.connect(DB_FILE)
    con.executescript(SCHEMA.read_text(encoding='utf-8'))
    return con


def ingest_subsystem(con, row: dict):
    sid = row.get('id') or row.get('name') or '?'
    con.execute(
        'INSERT OR REPLACE INTO subsystems(id,name,dir,provider,udts_path,tags_path,host) '
        'VALUES (?,?,?,?,?,?,?)',
        (sid,
         sid.split(' ', 1)[-1] if ' ' in sid else sid,
         row.get('dir'),
         row.get('provider'),
         row.get('udts'),
         row.get('tags'),
         row.get('host')),
    )
    for ns in row.get('namespaces') or []:
        con.execute(
            'INSERT OR IGNORE INTO subsystem_namespaces(subsystem_id,namespace) '
            'VALUES (?,?)',
            (sid, ns),
        )


def field_attrs(v):
    """Normalize heterogeneous UDT field spec into (type, nullable, array, desc)."""
    if isinstance(v, str):
        return v, 0, 0, None
    if isinstance(v, dict):
        return (
            v.get('t') or v.get('type') or 'any',
            1 if v.get('nullable') else 0,
            1 if v.get('array') else 0,
            v.get('desc'),
        )
    return str(v), 0, 0, None


def ingest_udts(con, subsystem_id, udts_json_path: Path):
    data = load_json(udts_json_path)
    if not data:
        return 0
    types = data.get('types') or {}
    n = 0
    for name, spec in types.items():
        con.execute(
            'INSERT OR REPLACE INTO udts(name,subsystem_id,glyph,base,desc,layer,raw) '
            'VALUES (?,?,?,?,?,?,?)',
            (name, subsystem_id,
             spec.get('glyph'), spec.get('base') or spec.get('extends'),
             spec.get('desc'), spec.get('layer'),
             json.dumps(spec, ensure_ascii=False, sort_keys=True)),
        )
        fields = spec.get('fields') or {}
        # support both dict of {name:type} and list of {name,type,...}
        if isinstance(fields, dict):
            items = list(fields.items())
        else:
            items = [(f.get('name') or f.get('n'), f) for f in fields]
        for pos, (fname, fval) in enumerate(items):
            if not fname:
                continue
            ftype, nullable, is_array, fdesc = field_attrs(fval)
            con.execute(
                'INSERT OR REPLACE INTO udt_fields'
                '(udt,name,type,nullable,is_array,position,desc) '
                'VALUES (?,?,?,?,?,?,?)',
                (name, fname, ftype, nullable, is_array, pos, fdesc),
            )
        n += 1
    return n


def ingest_tags(con, subsystem_id, tags_json_path: Path):
    data = load_json(tags_json_path)
    if not data:
        return 0
    rows = data.get('tags') or []
    n = 0
    for t in rows:
        path = t.get('path')
        patt = t.get('pathPattern')
        if not path and not patt:
            continue
        con.execute(
            'INSERT INTO tags(path,path_pattern,type,cardinality,unit,desc,subsystem_id) '
            'VALUES (?,?,?,?,?,?,?)',
            (path, patt,
             t.get('type'),
             t.get('cardinality') or ('many' if patt else 'one'),
             t.get('unit'),
             t.get('desc'),
             subsystem_id),
        )
        n += 1
    return n


def ingest_programs(con):
    prog_dir = ROOT / 'controls' / 'scada' / 'programs'
    if not prog_dir.exists():
        return 0
    n = 0
    for p in sorted(prog_dir.rglob('*.json')):
        data = load_json(p)
        if not data:
            continue
        rel = p.relative_to(ROOT).as_posix()
        # Some manifests reuse 🏗️ as a nested UDT block; coerce to string.
        def s(v):
            return v if isinstance(v, str) or v is None else json.dumps(v, ensure_ascii=False)
        con.execute(
            'INSERT OR REPLACE INTO programs(file,section,glyph,name,module,desc,raw) '
            'VALUES (?,?,?,?,?,?,?)',
            (rel,
             s(data.get('§')),
             s(data.get('🏗️')),
             s(data.get('name')),
             s(data.get('module')),
             s(data.get('desc')),
             json.dumps(data, ensure_ascii=False, sort_keys=True)),
        )
        n += 1
    return n


def dump_sql(con, out: Path):
    """Human-readable dump for git diffs."""
    lines = ['-- AUTO-GENERATED by controls/db/build.py · do not hand-edit.\n',
             '-- Source of truth = JSON manifests; rebuild with `python3 controls/db/build.py`.\n\n']
    for line in con.iterdump():
        # skip the noisy BEGIN/COMMIT TRANSACTION wrappers
        if line.strip() in ('BEGIN TRANSACTION;', 'COMMIT;'):
            continue
        lines.append(line + '\n')
    out.write_text(''.join(lines), encoding='utf-8')


def main():
    if not SCHEMA.exists():
        print(f'!!  schema missing: {SCHEMA}', file=sys.stderr)
        sys.exit(2)

    reg = load_json(REGISTRY)
    if not reg:
        print(f'!!  registry missing: {REGISTRY}', file=sys.stderr)
        sys.exit(2)

    con = fresh_db()

    subs = reg.get('subsystems') or []
    udt_total = tag_total = 0
    for row in subs:
        ingest_subsystem(con, row)
        sid = row.get('id')
        udts = row.get('udts')
        if udts:
            udt_total += ingest_udts(con, sid, ROOT / udts)
        tags = row.get('tags')
        if tags:
            tag_total += ingest_tags(con, sid, ROOT / tags)

    prog_total = ingest_programs(con)
    con.commit()

    SEED_OUT.parent.mkdir(parents=True, exist_ok=True)
    dump_sql(con, SEED_OUT)
    con.close()

    size = DB_FILE.stat().st_size
    print(f'✓ {DB_FILE.relative_to(ROOT)}   {size:>7,} bytes')
    print(f'✓ {SEED_OUT.relative_to(ROOT)}')
    print(f'  subsystems: {len(subs)}  udts: {udt_total}  tags: {tag_total}  programs: {prog_total}')


if __name__ == '__main__':
    main()
