#!/usr/bin/env node
/**
 * ACG Paper Auto-Index — parser
 *
 * Scans the repo for files containing `acg-paper:` frontmatter (HTML comments,
 * YAML frontmatter in markdown, or .meta.yml sidecars), parses the metadata,
 * auto-fills missing optional fields, and writes papers.json.
 *
 * See: docs/engineering/standards/paper-auto-index.md
 */
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const REPO_ROOT = path.resolve(__dirname, '..', '..');
const PAPERS_JSON = path.join(REPO_ROOT, 'papers.json');

const REQUIRED = ['title', 'author', 'type', 'abstract'];
const VALID_TYPES = new Set([
  'white-paper', 'position-paper', 'experimental',
  'research-note', 'knowledge', 'standard'
]);
const VALID_STATUS = new Set(['draft', 'review', 'published', 'archived']);
const TYPE_LABELS = {
  'white-paper':    'White Paper',
  'position-paper': 'Position Paper',
  'experimental':   'Experimental',
  'research-note':  'Research Note',
  'knowledge':      'Knowledge About Knowledge',
  'standard':       'Standard',
};
const TAG_VOCABULARY = new Set([
  // core
  'ai-safety','governance','testing','ethics','architecture','automation',
  'calibration','peer-review','culture','epistemics','falsification',
  'consciousness','harness','federation','healthcare','standards',
  // technical
  'blockchain','konomi','isa-88','isa-95','packml','scada','opc-ua',
  'guild-chain','guild-ops','webrtc','p2p','github-actions','ci-cd',
  // meta
  'knowledge-about-knowledge','systems-thinking','cognitive-apprenticeship',
  'triad-engine','toast','occam','indexing','white-papers'
]);

// Skip these directories entirely. The Guild's own docs/engineering/standards
// files carry acg-paper frontmatter and ARE meant to be indexed. But copies
// of those standards (test fixtures, app snapshots, node_modules) must be
// excluded so the validator doesn't see duplicate IDs.
const SKIP_DIRS = new Set([
  '.git', 'node_modules', 'guild/web/dist', '__pycache__',
  'guild/Enterprise/L2/hmi/web/components/udts', 'guild/Enterprise/L2/hmi/web/components/tags',
  'guild/apps/test',         // test-app snapshots duplicate standard IDs
  'guild/apps/p2p',          // p2p guild app (upstream ACGP2P snapshot)
  'guild/Enterprise',        // controls tree (contains its own standards)
  'guild/Enterprise/L2/hmi/web/views/data',    // body content for route views
  'guild/apps/whitepapers/data'
]);

// ── File walking ────────────────────────────────────────────────

function walkFiles(dir, out = []) {
  const rel = path.relative(REPO_ROOT, dir).split(path.sep).join('/');
  for (const skip of SKIP_DIRS) {
    if (rel === skip || rel.startsWith(skip + '/')) return out;
  }
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); }
  catch { return out; }
  for (const ent of entries) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) walkFiles(full, out);
    else if (/\.(html|md|yml|yaml)$/i.test(ent.name)) out.push(full);
  }
  return out;
}

// ── Frontmatter extraction ──────────────────────────────────────

/** Extract YAML block from HTML comment in first 50 lines. */
function extractFromHTML(text) {
  const head = text.split('\n').slice(0, 50).join('\n');
  const m = /<!--([\s\S]*?)-->/g.exec(head);
  if (!m) return null;
  const inner = m[1].trim();
  if (!/^\s*acg-paper:/m.test(inner)) return null;
  return inner;
}

/** Extract YAML frontmatter from markdown. */
function extractFromMarkdown(text) {
  const m = /^---\s*\n([\s\S]*?)\n---/.exec(text);
  if (!m) return null;
  if (!/^\s*acg-paper:/m.test(m[1])) return null;
  return m[1];
}

/** For .meta.yml sidecars — whole file is the YAML. */
function extractFromYamlFile(text) {
  if (!/^\s*acg-paper:/m.test(text)) return null;
  return text;
}

function parsePaperBlock(yamlText) {
  try {
    const doc = yaml.load(yamlText);
    return doc && doc['acg-paper'] ? doc['acg-paper'] : null;
  } catch (e) {
    console.warn(`  [warn] YAML parse error: ${e.message}`);
    return null;
  }
}

// ── Auto-fill ───────────────────────────────────────────────────

function nextId(existingPapers) {
  let max = 0;
  for (const p of existingPapers) {
    const m = /ACG-WP-(\d+)-\d+/.exec(p.id || '');
    if (m) max = Math.max(max, parseInt(m[1], 10));
  }
  const year = new Date().getUTCFullYear();
  return `ACG-WP-${String(max + 1).padStart(3, '0')}-${year}`;
}

function extractTags(text) {
  const low = text.toLowerCase();
  const hits = [];
  for (const tag of TAG_VOCABULARY) {
    if (low.includes(tag)) hits.push(tag);
  }
  return hits;
}

function slugify(s) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function normalizeDate(v) {
  if (!v) return null;
  // YAML may parse dates as Date objects or as ISO strings
  if (v instanceof Date) return v.toISOString().slice(0, 10);
  const s = String(v);
  // Match YYYY-MM-DD prefix
  const m = /^(\d{4}-\d{2}-\d{2})/.exec(s);
  return m ? m[1] : s;
}

function fillDefaults(p, filePath, existingPapers) {
  const today = new Date().toISOString().slice(0, 10);
  if (!p.id)     p.id = nextId(existingPapers);
  p.date = normalizeDate(p.date) || today;
  if (!p.status) p.status = 'draft';
  if (!p.slug)   p.slug = path.basename(filePath).replace(/\.[^.]+$/, '');
  if (!p.tags || p.tags.length === 0) {
    p.tags = extractTags(`${p.title || ''} ${p.abstract || ''}`);
  }
  // Normalize abstract — strip trailing newlines
  if (p.abstract) p.abstract = String(p.abstract).trim();
  return p;
}

function validate(p, filePath, warnings) {
  for (const field of REQUIRED) {
    if (!p[field]) {
      warnings.push({ file: filePath, issue: `missing required field: ${field}` });
      return false;
    }
  }
  if (!VALID_TYPES.has(p.type)) {
    warnings.push({ file: filePath, issue: `invalid type: ${p.type}` });
    return false;
  }
  if (!VALID_STATUS.has(p.status)) {
    warnings.push({ file: filePath, issue: `invalid status: ${p.status}` });
    return false;
  }
  return true;
}

// ── Main ────────────────────────────────────────────────────────

function main() {
  console.log('[parse-papers] scanning repo...');

  // Load existing papers.json (for ID continuity)
  let existing = [];
  if (fs.existsSync(PAPERS_JSON)) {
    try { existing = JSON.parse(fs.readFileSync(PAPERS_JSON, 'utf8')); } catch {}
  }

  const files = walkFiles(REPO_ROOT);
  const papers = [];
  const warnings = [];
  const newPapers = [];

  for (const file of files) {
    const rel = path.relative(REPO_ROOT, file).split(path.sep).join('/');
    const text = fs.readFileSync(file, 'utf8');

    let yamlText = null;
    if (/\.html$/i.test(file))      yamlText = extractFromHTML(text);
    else if (/\.md$/i.test(file))   yamlText = extractFromMarkdown(text);
    else if (/\.(ya?ml)$/i.test(file)) yamlText = extractFromYamlFile(text);
    if (!yamlText) continue;

    const paper = parsePaperBlock(yamlText);
    if (!paper) continue;

    // Fill + validate
    fillDefaults(paper, file, [...existing, ...papers]);
    if (!validate(paper, rel, warnings)) continue;

    paper.source_file = rel;
    paper.url = `https://aicraftspeopleguild.github.io/${paper.slug}.html`;

    const wasNew = !existing.find(p => p.id === paper.id);
    if (wasNew) newPapers.push(paper);
    papers.push(paper);
  }

  // Sort: type order → date desc → title asc
  const typeOrder = Array.from(VALID_TYPES);
  papers.sort((a, b) => {
    const ta = typeOrder.indexOf(a.type);
    const tb = typeOrder.indexOf(b.type);
    if (ta !== tb) return ta - tb;
    if (a.date !== b.date) return b.date.localeCompare(a.date);
    return (a.title || '').localeCompare(b.title || '');
  });

  fs.writeFileSync(PAPERS_JSON, JSON.stringify(papers, null, 2) + '\n', 'utf8');
  console.log(`[parse-papers] indexed ${papers.length} papers (${newPapers.length} new)`);
  if (warnings.length) {
    console.log(`[parse-papers] ${warnings.length} warnings:`);
    for (const w of warnings) console.log(`  ${w.file}: ${w.issue}`);
  }

  // Write new-papers list for the PR comment step
  fs.writeFileSync(
    path.join(REPO_ROOT, '.paper-index-summary.json'),
    JSON.stringify({ newPapers, warnings, total: papers.length }, null, 2),
    'utf8'
  );
}

if (require.main === module) {
  try { main(); } catch (e) { console.error(e); process.exit(1); }
}

module.exports = { main };
