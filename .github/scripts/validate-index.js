#!/usr/bin/env node
/**
 * ACG Paper Auto-Index — validator
 *
 * Runs after parse-papers.js. Checks papers.json for:
 *   - duplicate IDs
 *   - invalid ISO 8601 dates
 *   - invalid type or status enums
 *   - source_file exists on disk
 *
 * Exits non-zero on failure.
 */
const fs = require('fs');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '..', '..');
const PAPERS_JSON = path.join(REPO_ROOT, 'papers.json');

const VALID_TYPES = new Set([
  'white-paper', 'position-paper', 'experimental',
  'research-note', 'knowledge', 'standard'
]);
const VALID_STATUS = new Set(['draft', 'review', 'published', 'archived']);
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;

function main() {
  if (!fs.existsSync(PAPERS_JSON)) {
    console.error('[validate] papers.json not found');
    process.exit(1);
  }
  const papers = JSON.parse(fs.readFileSync(PAPERS_JSON, 'utf8'));

  const errors = [];
  const seenIds = new Set();
  const seenSlugs = new Set();

  for (const p of papers) {
    // Duplicate ID
    if (p.id && seenIds.has(p.id)) errors.push(`duplicate id: ${p.id}`);
    seenIds.add(p.id);

    // Duplicate slug
    if (p.slug && seenSlugs.has(p.slug)) errors.push(`duplicate slug: ${p.slug} (${p.id})`);
    seenSlugs.add(p.slug);

    // Date format
    if (!ISO_DATE.test(p.date)) errors.push(`${p.id}: invalid date "${p.date}"`);

    // Type / status enums
    if (!VALID_TYPES.has(p.type))    errors.push(`${p.id}: invalid type "${p.type}"`);
    if (!VALID_STATUS.has(p.status)) errors.push(`${p.id}: invalid status "${p.status}"`);

    // Source file exists
    if (p.source_file) {
      const full = path.join(REPO_ROOT, p.source_file);
      if (!fs.existsSync(full)) errors.push(`${p.id}: source_file missing "${p.source_file}"`);
    }

    // Required fields
    for (const f of ['title', 'author', 'type', 'abstract']) {
      if (!p[f]) errors.push(`${p.id}: missing required field "${f}"`);
    }
  }

  if (errors.length) {
    console.error(`[validate] FAILED with ${errors.length} errors:`);
    for (const e of errors) console.error(`  - ${e}`);
    process.exit(1);
  }
  console.log(`[validate] ✓ ${papers.length} papers valid`);
}

if (require.main === module) {
  try { main(); } catch (e) { console.error(e); process.exit(1); }
}

module.exports = { main };
