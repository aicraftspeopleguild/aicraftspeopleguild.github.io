# /controls/db

🗄️  Canonical tag / UDT / subsystem catalog **plus** the live tag
snapshot read by the README HMI.

```
db/
  tags.json       live runtime snapshot — rendered as shields.io badges
                   on the README; maintained by /controls/scada/gateway/
                   workflows/sync-db.yml from acg-db-labelled issues
  tags.sqlite     indexed catalog · subsystems × UDTs × tags × programs
                   built by build.py from every JSON manifest
  sql/
    schema.sql    CREATE TABLE statements (source-of-truth DDL)
    seed.sql     AUTO-GENERATED text dump of tags.sqlite · diff-friendly
  build.py        python3 controls/db/build.py · rebuilds tags.sqlite + seed.sql
```

## tags.json — live HMI source (read path)

The README uses `shields.io`'s `dynamic/json` endpoint to render live
badges out of `tags.json`:

```
https://img.shields.io/badge/dynamic/json
  ?url=https://teslasolar.github.io/ACGP2P/controls/db/tags.json
  &query=$.room.peerCount.value
  &label=peers&color=1a5c4c
```

Every tag in the snapshot follows the same shape so `$.<ns>.<key>.value`
always works:

```jsonc
{
  "room": {
    "peerCount": { "value": 1, "quality": "good", "type": "Counter" }
  }
}
```

## tags.sqlite — indexed catalog

Same data you could glean from walking every `udts.json` + `tags.json` +
`providers/registry.json`, but in one file with indexes and joins.
Schema tables:

- `subsystems` — one row per registered provider
- `subsystem_namespaces` — which `<ns>.*` paths each subsystem owns
- `udts` + `udt_fields` — every UDT declared across the project
- `tags` — catalog of every tag path (or `pathPattern` for dynamic keys)
- `programs` — every `controls/scada/programs/**/*.json` manifest

Three convenience **views** give common joins:

- `v_subsystem_summary` — id, provider, udt_count, tag_count, namespaces
- `v_udt_rollup` — udt name + comma-joined `field:type` list
- `v_tags_full` — tag + type + cardinality + owning subsystem

Current counts (rebuild-to-verify): 10 subsystems · 35 UDTs · 80 tags
· 16 program manifests.

### Quick queries

```bash
sqlite3 controls/db/tags.sqlite
```

```sql
-- who owns the auth.* namespace?
SELECT * FROM v_tags_full WHERE path_or_pattern LIKE 'auth.%';

-- every UDT with a Base field
SELECT name, base FROM udts WHERE base IS NOT NULL;

-- dynamic tag patterns
SELECT path_pattern, type, subsystem_id FROM tags WHERE cardinality='many';

-- full summary
SELECT * FROM v_subsystem_summary;

-- count of tags per namespace
SELECT n.namespace, COUNT(*) AS tags
  FROM subsystem_namespaces n
  LEFT JOIN tags t ON t.subsystem_id = n.subsystem_id
  GROUP BY n.namespace ORDER BY tags DESC;
```

## Rebuild

```bash
python3 controls/db/build.py
```

The script:

1. Reads `controls/scada/gateway/providers/registry.json`.
2. For each subsystem, ingests its `udts.json` + `tags.json`.
3. Walks `controls/scada/programs/**/*.json` into `programs`.
4. Writes `tags.sqlite` (binary, committed) and `sql/seed.sql` (text
   dump — use this to review catalog changes in git diffs).

A GitHub Action rebuilds on every push that touches a manifest; see
`.github/workflows/rebuild-db.yml`.

## Write path (live snapshot)

Two routes, pick one:

1. **Commit directly** — edit `tags.json` in a PR. The HMI re-renders as
   soon as Pages redeploys (~60 s).
2. **File an issue** — use the forms under `.github/ISSUE_TEMPLATE/`:
   - `tag-update.yml` — one tag path + value
   - `log-entry.yml`  — append to `errors.ring`
   - `control-action.yml` — request a runtime action

   The sync workflow parses the issue body, merges into `tags.json`, and
   commits back to main. Issues are the audit log.

## Compressed-token format (`§0`)

Every tag write can also be expressed in the dense glyph spec from
`controls/scada/00-legend.json`. Example:

```
🏷️ room.peerCount  = 7                🟢 type:Counter  ts:now
🏷️ tracker.state   = "connected"      🟢 type:String   ts:now
🏷️ errors.count    = 12               🟡 type:Counter  ts:now-5m
```
