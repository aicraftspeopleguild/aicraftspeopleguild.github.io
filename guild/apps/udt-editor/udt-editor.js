// ═══ ACG UDT editor · compressed tag-DB form ═══
// Loads a UDT template (L3/udts/<name>/template.json) + a named instance
// (L3/udts/<name>/instances/<id>.json), renders a dense, type-aware grid
// of every parameter, tracks dirty fields, and writes changes back
// through the same cmd:tag-write flow the control-deck uses.
//
// URL hash: #udt=machine&instance=line-1

// ─── self-detect the GitHub repo we're hosted from ───────────────────
function detectRepo() {
  const q = new URLSearchParams(location.hash.slice(1));
  const override = q.get('repo');
  if (override && /^[\w.-]+\/[\w.-]+$/.test(override)) return override;
  const host = location.hostname;
  if (host.endsWith('.github.io')) {
    const owner = host.replace(/\.github\.io$/, '');
    const first = (location.pathname.split('/').filter(Boolean)[0]) || '';
    if (first.endsWith('.github.io')) return `${owner}/${first}`;
    return `${owner}/${host}`;
  }
  return 'teslasolar/aicraftspeopleguild.github.io';
}
const REPO = detectRepo();

// ─── tiny helpers ────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const TOK_KEY = 'acg_gh_pat';
const loadTok = () => localStorage.getItem(TOK_KEY) || '';
const saveTok = t => t ? localStorage.setItem(TOK_KEY, t) : localStorage.removeItem(TOK_KEY);

function log(msg, cls = 'info') {
  const el = $('log');
  if (!el) return;
  const line = document.createElement('div');
  line.className = cls;
  const ts = new Date().toTimeString().slice(0, 8);
  line.textContent = `${ts} · ${msg}`;
  el.appendChild(line);
  el.scrollTop = el.scrollHeight;
}

async function gh(method, path, body) {
  const tok = loadTok();
  const r = await fetch('https://api.github.com' + path, {
    method,
    headers: {
      'Accept': 'application/vnd.github+json',
      'Content-Type': 'application/json',
      ...(tok ? { Authorization: 'token ' + tok } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(`GitHub ${method} ${path} → HTTP ${r.status}`);
  return r.json();
}

function paintAuth() {
  const chip = $('auth-chip'), txt = $('auth-text');
  const tok = loadTok();
  if (tok) {
    chip.className = 'auth on';
    txt.textContent = 'PAT set · direct writes enabled';
  } else {
    chip.className = 'auth off';
    txt.textContent = 'paste PAT to enable direct writes (else falls back to issue-form link)';
  }
}

// ─── template + instance loaders ─────────────────────────────────────
const TPL_BASE = '../../Enterprise/L3/udts';

async function loadTemplate(udt) {
  return fetch(`${TPL_BASE}/${udt}/template.json`, { cache: 'no-store' }).then(r => r.json());
}
async function loadInstance(udt, inst) {
  try {
    return await fetch(`${TPL_BASE}/${udt}/instances/${inst}.json`, { cache: 'no-store' }).then(r => r.json());
  } catch {
    return { udtType: udt, instance: inst, parameters: {} };
  }
}
async function loadInstanceIndex(udt) {
  try {
    return await fetch(`${TPL_BASE}/${udt}/instances/_index.json`, { cache: 'no-store' }).then(r => r.json());
  } catch {
    return { instances: [] };
  }
}
async function populateInstanceSelect(udt, selected) {
  const sel = $('sel-inst');
  const idx = await loadInstanceIndex(udt);
  sel.innerHTML = '';
  const items = idx.instances && idx.instances.length ? idx.instances : [{ slug: 'line-1', id: 'line-1' }];
  for (const it of items) {
    const o = document.createElement('option');
    o.value = it.slug;
    const label = it.name || it.id || it.slug;
    o.textContent = label.length > 48 ? label.slice(0, 46) + '…' : label;
    if (it.slug === selected) o.selected = true;
    sel.appendChild(o);
  }
  if (!sel.value && items[0]) sel.value = items[0].slug;
}

// ─── form renderer ───────────────────────────────────────────────────
const state = {
  udt: null,          // the loaded template
  inst: null,         // the loaded instance
  orig: {},           // original value per field, for dirty-diff
  cur: {},            // current edited value per field
  dirty: new Set(),   // field names that differ from orig
  writes: 0,
};

function isoOrEmpty(v) { return v || ''; }

function renderField(name, spec, val) {
  const dt = (spec.dataType || 'String').toLowerCase();
  const dirty = state.dirty.has(name);
  const wrap = document.createElement('div');
  wrap.className = 'row' + (dirty ? ' dirty' : '');
  wrap.dataset.field = name;

  const lbl = document.createElement('span');
  lbl.className = 'lbl' + (spec.required ? ' req' : '');
  lbl.textContent = name;
  lbl.title = spec.description || name;
  wrap.appendChild(lbl);

  const typ = document.createElement('span');
  typ.className = 'typ';
  typ.textContent = (spec.dataType || 'String') + (spec.unit ? ` · ${spec.unit}` : '');
  wrap.appendChild(typ);

  const w = document.createElement('div');
  w.className = 'wrap';

  let inp;
  if (spec.enum) {
    inp = document.createElement('select');
    for (const opt of spec.enum) {
      const o = document.createElement('option');
      o.value = opt; o.textContent = opt;
      if (String(val) === opt) o.selected = true;
      inp.appendChild(o);
    }
  } else if (dt === 'boolean') {
    inp = document.createElement('input');
    inp.type = 'checkbox';
    inp.checked = !!val;
  } else if (dt === 'number' || dt === 'counter') {
    inp = document.createElement('input');
    inp.type = 'number';
    if (spec.min != null) inp.min = spec.min;
    if (spec.max != null) inp.max = spec.max;
    inp.step = 'any';
    inp.value = val ?? '';
  } else if (dt === 'datetime') {
    inp = document.createElement('input');
    inp.type = 'text';
    inp.value = isoOrEmpty(val);
    inp.placeholder = 'YYYY-MM-DDThh:mm:ssZ';
  } else {
    inp = document.createElement('input');
    inp.type = 'text';
    inp.value = val ?? '';
  }
  inp.addEventListener('input', () => onEdit(name, inp, dt));
  inp.addEventListener('change', () => onEdit(name, inp, dt));
  w.appendChild(inp);

  if (spec.unit && dt !== 'boolean') {
    const u = document.createElement('span');
    u.className = 'unit';
    u.textContent = spec.unit;
    w.appendChild(u);
  }
  wrap.appendChild(w);
  return wrap;
}

function readInput(inp, dt) {
  if (inp.type === 'checkbox') return inp.checked;
  if (dt === 'number' || dt === 'counter') return inp.value === '' ? null : Number(inp.value);
  return inp.value;
}

function eq(a, b) {
  if (a === b) return true;
  if (a == null && b === '') return true;
  if (b == null && a === '') return true;
  return String(a ?? '') === String(b ?? '');
}

function onEdit(name, inp, dt) {
  const v = readInput(inp, dt);
  state.cur[name] = v;
  const dirtyNow = !eq(state.orig[name], v);
  const row = inp.closest('.row');
  if (dirtyNow) { state.dirty.add(name); row.classList.add('dirty'); }
  else { state.dirty.delete(name); row.classList.remove('dirty'); }
  $('n-dirty').textContent = state.dirty.size;
}

function render() {
  const host = $('form-host');
  host.innerHTML = '';
  const { udt, inst } = state;
  const params = udt.parameters || {};
  const sections = udt.sections || [
    { id: 'all', title: udt.udtType, fields: Object.keys(params) },
  ];
  let total = 0;
  for (const sec of sections) {
    const div = document.createElement('div');
    div.className = 'sect';
    const h = document.createElement('h2');
    h.textContent = sec.title;
    div.appendChild(h);
    const grid = document.createElement('div');
    grid.className = 'grid';
    for (const f of sec.fields) {
      if (!params[f]) continue;
      const val = state.cur[f];
      grid.appendChild(renderField(f, params[f], val));
      total++;
    }
    div.appendChild(grid);
    host.appendChild(div);
  }
  $('n-fields').textContent = total;
  $('n-dirty').textContent = state.dirty.size;
  $('n-writes').textContent = state.writes;
}

// ─── load + init ─────────────────────────────────────────────────────
async function boot() {
  paintAuth();
  $('tok').addEventListener('input', e => { saveTok(e.target.value.trim()); paintAuth(); });
  const t = loadTok();
  if (t) $('tok').value = t;

  const q = new URLSearchParams(location.hash.slice(1));
  const udtName = q.get('udt') || $('sel-udt').value;
  $('sel-udt').value = udtName;
  await populateInstanceSelect(udtName, q.get('instance'));
  const inst = $('sel-inst').value;

  try {
    state.udt = await loadTemplate(udtName);
    state.inst = await loadInstance(udtName, inst);
    state.orig = { ...(state.inst.parameters || {}) };
    state.cur = { ...(state.inst.parameters || {}) };
    state.dirty = new Set();
    render();
    log(`loaded ${udtName}/${inst} · ${Object.keys(state.udt.parameters).length} fields`, 'ok');
    log(`repo · ${REPO}`, 'info');
  } catch (e) {
    log('✗ ' + e.message, 'err');
  }

  $('btn-reset').addEventListener('click', () => {
    state.cur = { ...state.orig };
    state.dirty = new Set();
    render();
    log('reset to original', 'info');
  });
  $('btn-save').addEventListener('click', saveDirty);

  $('sel-udt').addEventListener('change', () => {
    location.hash = `udt=${$('sel-udt').value}&instance=${$('sel-inst').value}`;
    location.reload();
  });
  $('sel-inst').addEventListener('change', () => {
    location.hash = `udt=${$('sel-udt').value}&instance=${$('sel-inst').value}`;
    location.reload();
  });

  const ref = document.referrer;
  if (ref && !ref.includes('/udt-editor/')) {
    const back = $('back-chip');
    back.href = ref;
    back.textContent = '↩ back';
    back.style.display = '';
  }
}

// ─── save · one cmd:tag-write issue per dirty field ──────────────────
async function saveDirty() {
  if (state.dirty.size === 0) { log('nothing dirty', 'warn'); return; }
  const tagRoot = (state.udt.tagRoot || `udt.${state.udt.udtType.toLowerCase()}.{id}`)
    .replace('{id}', state.inst.instance);

  const tok = loadTok();
  if (!tok) {
    // Fallback — open a bulk tag-write issue form with every dirty field.
    const patch = {};
    for (const f of state.dirty) patch[f] = state.cur[f];
    const title = `cmd:udt-write udt=${state.udt.udtType} instance=${state.inst.instance}`;
    const body = '```json\n' + JSON.stringify({ tagRoot, patch }, null, 2) + '\n```';
    const url = `https://github.com/${REPO}/issues/new?` + new URLSearchParams({ title, body, labels: 'cmd' });
    window.open(url, '_blank');
    log('opened bulk udt-write issue form (no PAT)', 'info');
    return;
  }

  log(`writing ${state.dirty.size} dirty field(s) to ${REPO} …`, 'info');
  let ok = 0, fail = 0;
  for (const f of [...state.dirty]) {
    const path = `${tagRoot}.${f}`;
    const value = state.cur[f];
    const spec = state.udt.parameters[f] || {};
    const title = `cmd:tag-write path=${path} value=${value}`;
    const body = JSON.stringify({ type: spec.dataType || 'String', unit: spec.unit, quality: 'good' });
    try {
      const res = await gh('POST', `/repos/${REPO}/issues`, { title, body, labels: ['cmd', 'tag', 'udt'] });
      log(`✓ #${res.number} · ${f}`, 'ok');
      state.orig[f] = state.cur[f];
      state.dirty.delete(f);
      state.writes++;
      ok++;
    } catch (e) {
      log(`✗ ${f} · ${e.message}`, 'err');
      fail++;
    }
  }
  render();
  log(`done · ${ok} ok, ${fail} fail · workflow picks these up`, fail ? 'warn' : 'ok');
}

boot();
