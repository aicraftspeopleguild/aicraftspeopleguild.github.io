#!/usr/bin/env node
/**
 * PR comment for the Paper Auto-Index workflow.
 *
 * Usage (inside a workflow step with github-script@v7):
 *   const post = require('./.github/scripts/pr-comment.js');
 *   await post({ github, context });
 *
 * Reads `.paper-index-summary.json` produced by parse-papers.js and posts
 * a markdown comment on the PR. No-ops if the summary file is missing.
 */
const fs = require('fs');

module.exports = async ({ github, context }) => {
  let s;
  try { s = JSON.parse(fs.readFileSync('.paper-index-summary.json', 'utf8')); }
  catch { return console.log('no summary — skipping PR comment'); }

  const L = [`## 📚 Paper Auto-Index`, ''];
  L.push(`Indexed **${s.total}** paper${s.total === 1 ? '' : 's'} total.`);

  if (s.newPapers?.length) {
    L.push('', '### New this PR', '');
    for (const p of s.newPapers) {
      L.push(`- ✓ **${p.title}** (${p.id})`);
      L.push(`  Type: ${p.type} · Tags: ${(p.tags || []).join(', ') || '—'}`);
    }
  }
  if (s.warnings?.length) {
    L.push('', '### ⚠️ Warnings', '');
    for (const w of s.warnings) L.push(`- \`${w.file}\`: ${w.issue}`);
  }

  await github.rest.issues.createComment({
    owner: context.repo.owner,
    repo:  context.repo.repo,
    issue_number: context.issue.number,
    body:  L.join('\n')
  });
};
