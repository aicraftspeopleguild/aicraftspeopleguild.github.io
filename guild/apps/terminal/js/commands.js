/* ═══════════════════════════════════════════════════════
   commands.js — COMMANDS registry
   Each key is an acg CLI command name; value is an async
   handler function that receives parsed args and writes
   to the terminal via ui.js helpers.
   ═══════════════════════════════════════════════════════ */
'use strict';

/* Depends on: config.js (ENDPOINTS), ui.js (line/blank/kv/esc/spinner/apiFetch/navPath/flattenTags) */

const COMMANDS = {};

/* ── help ────────────────────────────────────────────── */
COMMANDS['help'] = COMMANDS['acg'] = async () => {
  line('<span class="line-head">⚒  ACG Guild Terminal</span>');
  blank();
  line('  <span class="line-dim">Commands mirror the real <code>acg</code> CLI. Data is live from GitHub Pages.</span>');
  blank();
  const cmds = [
    ['health',                   'Enterprise vitals — paperCount · memberCount · apiVersion'],
    ['papers:list',              'Paper catalog — titles, authors, dates'],
    ['papers:list q=<text>',     'Filter papers by title / author'],
    ['state:summary',            'Runtime state — tag counts, tool runs, faults'],
    ['state:faults',             'Active faults — tool failures, pipeline aborts'],
    ['tag:read tag=<path>',      'Read a runtime tag (e.g. enterprise.paperCount)'],
    ['tag:read prefix=<ns>',     'List all tags under a namespace'],
    ['api:list',                 'Live API endpoint URLs'],
    ['git:log',                  'Recent commits via GitHub API'],
    ['clear',                    'Clear the terminal'],
    ['help',                     'This message'],
  ];
  const maxLen = Math.max(...cmds.map(([c]) => c.length));
  for (const [cmd, desc] of cmds) {
    line(`  <span class="line-key">${cmd.padEnd(maxLen + 2)}</span><span class="line-dim">${desc}</span>`);
  }
  blank();
  line('  <span class="line-dim">Tip: use ↑ / ↓ to navigate history · Tab to complete</span>');
};

/* ── health ──────────────────────────────────────────── */
COMMANDS['health'] = async () => {
  const done = spinner();
  try {
    const d = await apiFetch(ENDPOINTS.health);
    done();
    blank();
    kv('paperCount ', d.paperCount,  d.paperCount  > 0 ? 'line-ok'  : 'line-dim');
    kv('memberCount', d.memberCount, d.memberCount > 0 ? 'line-ok'  : 'line-dim');
    kv('apiVersion ', d.apiVersion,  'line-purple');
    kv('lastUpdated', d.lastUpdated, 'line-dim');
    kv('source     ', d.source,      'line-dim');
    blank();
    line('  <span class="badge badge-ok">● LIVE</span>');
  } catch (e) {
    done();
    line(`  <span class="line-err">✗ ${esc(e.message)}</span>`);
  }
  blank();
};

/* ── papers:list ─────────────────────────────────────── */
COMMANDS['papers:list'] = async (args) => {
  const q = (args.q || args.query || '').toLowerCase();
  const done = spinner();
  try {
    const papers = await apiFetch(ENDPOINTS.papers);
    done();
    const filtered = q
      ? papers.filter(p =>
          (p.title   || '').toLowerCase().includes(q) ||
          (p.author  || '').toLowerCase().includes(q) ||
          (p.abstract|| '').toLowerCase().includes(q))
      : papers;
    blank();
    line(`  <span class="line-head">${filtered.length} paper${filtered.length !== 1 ? 's' : ''}${q ? ` matching "${esc(q)}"` : ''}</span>`);
    blank();
    for (const p of filtered) {
      const status = p.status === 'published'
        ? `<span class="badge badge-ok">published</span>`
        : `<span class="badge badge-warn">${esc(p.status || '?')}</span>`;
      line(`  <span class="tbl-id">${esc(p.doc_number || p.id || '—')}</span>  ${status}`);
      line(`    <span class="line-val">${esc(p.title)}</span>`);
      if (p.author)   line(`    <span class="line-dim">${esc(p.author)} · ${esc(p.date || '')}</span>`);
      if (p.abstract) line(`    <span class="line-dim" style="font-style:italic">${esc(p.abstract.slice(0, 100))}${p.abstract.length > 100 ? '…' : ''}</span>`);
      blank();
    }
  } catch (e) {
    done();
    line(`  <span class="line-err">✗ ${esc(e.message)}</span>`);
    blank();
  }
};

/* ── state:summary ───────────────────────────────────── */
COMMANDS['state:summary'] = async () => {
  const done = spinner();
  try {
    const d = await apiFetch(ENDPOINTS.state);
    done();
    blank();
    kv('tag_values       ', d.tag_values         ?? d.summary?.tag_values         ?? '—');
    kv('tool_runs        ', d.tool_runs           ?? d.summary?.tool_runs          ?? '—');
    kv('tool_failures    ', d.tool_failures       ?? d.summary?.tool_failures      ?? '—',
       (d.tool_failures    || d.summary?.tool_failures    || 0) > 0 ? 'line-err' : 'line-ok');
    kv('pipeline_runs    ', d.pipeline_runs       ?? '—');
    kv('pipeline_failures', d.pipeline_failures   ?? '—',
       (d.pipeline_failures || 0) > 0 ? 'line-err' : 'line-ok');
    kv('faults_active    ', d.faults_active       ?? d.summary?.faults_active      ?? '—',
       (d.faults_active    || d.summary?.faults_active    || 0) > 0 ? 'line-err' : 'line-ok');
    kv('events           ', d.events ?? '—');
    if (d.last_event) {
      blank();
      line('  <span class="line-dim">last event</span>');
      kv('  at     ', d.last_event.at   || '—', 'line-dim');
      kv('  kind   ', d.last_event.kind || '—', 'line-dim');
      kv('  tag    ', d.last_event.tag  || '—', 'line-dim');
    }
    if (d.last_pipeline_run) {
      blank();
      line('  <span class="line-dim">last pipeline run</span>');
      kv('  id     ', d.last_pipeline_run.pipeline_id || '—', 'line-dim');
      kv('  at     ', d.last_pipeline_run.started_at  || '—', 'line-dim');
      const ok = d.last_pipeline_run.ok;
      kv('  result ', ok ? 'COMPLETE' : 'ABORTED', ok ? 'line-ok' : 'line-err');
    }
  } catch (e) {
    done();
    line(`  <span class="line-err">✗ ${esc(e.message)}</span>`);
  }
  blank();
};

/* ── state:faults ────────────────────────────────────── */
COMMANDS['state:faults'] = async () => {
  const done = spinner();
  try {
    const d = await apiFetch(ENDPOINTS.state);
    done();
    const faults = d.faults || [];
    const active = faults.filter(f => f.active || f.cleared_at === null);
    blank();
    if (active.length === 0) {
      line('  <span class="line-ok">✓ No active faults</span>');
    } else {
      line(`  <span class="line-err">⚠ ${active.length} active fault${active.length !== 1 ? 's' : ''}</span>`);
      blank();
      for (const f of active) {
        const sev = f.severity === 'error'
          ? `<span class="badge badge-err">error</span>`
          : `<span class="badge badge-warn">${esc(f.severity || 'warn')}</span>`;
        line(`  <span class="line-key">#${f.fault_id}</span>  ${sev}  <span class="line-dim">${esc(f.tag)}</span>`);
        line(`    <span class="line-val">${esc(f.message)}</span>`);
        line(`    <span class="line-dim">raised ${esc(f.raised_at || '')}</span>`);
        blank();
      }
    }
  } catch (e) {
    done();
    line(`  <span class="line-err">✗ ${esc(e.message)}</span>`);
    blank();
  }
};

/* ── tag:read ────────────────────────────────────────── */
COMMANDS['tag:read'] = async (args) => {
  const tag    = args.tag    || args.path   || null;
  const prefix = args.prefix || null;
  if (!tag && !prefix) {
    line('  <span class="line-err">✗ usage: tag:read tag=&lt;name&gt;  or  tag:read prefix=&lt;namespace&gt;</span>');
    blank();
    return;
  }
  const done = spinner();
  try {
    const tags = await apiFetch(ENDPOINTS.tags);
    done();
    blank();
    if (tag) {
      const node = navPath(tags, tag);
      if (node === undefined) {
        line(`  <span class="line-err">✗ tag not found: ${esc(tag)}</span>`);
        line('  <span class="line-dim">Tip: use tag:read prefix=&lt;namespace&gt; to browse</span>');
      } else if (node && typeof node === 'object' && 'value' in node) {
        kv('tag      ', tag);
        kv('value    ', node.value    ?? '—', 'line-ok');
        kv('quality  ', node.quality  ?? '—', 'line-dim');
        kv('updated  ', node.updated_at || node.ts || '—', 'line-dim');
      } else if (typeof node === 'object') {
        const children = flattenTags(node, tag);
        line(`  <span class="line-dim">${esc(tag)} has ${children.length} tag${children.length !== 1 ? 's' : ''}:</span>`);
        blank();
        for (const t of children.slice(0, 40)) kv(`  ${t.path}`, t.value ?? '—', 'line-val');
        if (children.length > 40) line(`  <span class="line-dim">… ${children.length - 40} more</span>`);
      } else {
        kv(tag, node);
      }
    } else {
      const all     = flattenTags(tags);
      const matched = all.filter(t => t.path.startsWith(prefix));
      if (matched.length === 0) {
        line(`  <span class="line-err">✗ no tags found under prefix: ${esc(prefix)}</span>`);
      } else {
        line(`  <span class="line-dim">${matched.length} tag${matched.length !== 1 ? 's' : ''} under <span class="line-key">${esc(prefix)}</span></span>`);
        blank();
        const maxLen = Math.max(...matched.map(t => t.path.length));
        for (const t of matched.slice(0, 50)) {
          line(`  <span class="line-key">${t.path.padEnd(maxLen + 2)}</span><span class="line-val">${esc(t.value ?? '—')}</span><span class="line-dim">  ${esc(t.quality || '')}</span>`);
        }
        if (matched.length > 50) line(`  <span class="line-dim">… ${matched.length - 50} more</span>`);
      }
    }
  } catch (e) {
    done();
    line(`  <span class="line-err">✗ ${esc(e.message)}</span>`);
  }
  blank();
};

/* ── api:list ────────────────────────────────────────── */
COMMANDS['api:list'] = async () => {
  blank();
  line('  <span class="line-head">Live API endpoints</span>');
  blank();
  for (const [name, url] of Object.entries(ENDPOINTS)) {
    const rel = url.replace('https://teslasolar.github.io/aicraftspeopleguild.github.io', '');
    line(`  <span class="line-key">${name.padEnd(10)}</span>  <a href="${url}" target="_blank" style="color:var(--blue)">${esc(rel)}</a>`);
  }
  blank();
  line('  <span class="line-dim">All endpoints are CORS-open static JSON rebuilt on every push.</span>');
  blank();
};

/* ── git:log ─────────────────────────────────────────── */
COMMANDS['git:log'] = async () => {
  const done = spinner();
  try {
    const r = await fetch(
      'https://api.github.com/repos/aicraftspeopleguild/aicraftspeopleguild.github.io/commits?per_page=8',
      { headers: { Accept: 'application/vnd.github+json' } }
    );
    if (!r.ok) throw new Error(`GitHub API: HTTP ${r.status}`);
    const commits = await r.json();
    done();
    blank();
    line('  <span class="line-head">Recent commits</span>');
    blank();
    for (const c of commits) {
      const sha    = c.sha.slice(0, 7);
      const msg    = (c.commit.message.split('\n')[0] || '').slice(0, 72);
      const date   = (c.commit.author.date || '').slice(0, 10);
      const author = c.commit.author.name || '—';
      line(`  <span class="line-key">${sha}</span>  <span class="line-dim">${date}</span>  <span class="line-val">${esc(msg)}</span>`);
      line(`         <span class="line-dim">${esc(author)}</span>`);
    }
  } catch (e) {
    done();
    line(`  <span class="line-err">✗ ${esc(e.message)}</span>`);
    line('  <span class="line-dim">GitHub API rate-limits unauthenticated requests. Try again in a moment.</span>');
  }
  blank();
};

/* ── clear ───────────────────────────────────────────── */
COMMANDS['clear'] = async () => { out.innerHTML = ''; };
