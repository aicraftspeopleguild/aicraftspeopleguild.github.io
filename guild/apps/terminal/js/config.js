/* ═══════════════════════════════════════════════════════
   config.js — API base URL and endpoint map
   Self-detects base URL so the terminal works on both
   https://teslasolar.github.io/aicraftspeopleguild.github.io/
   and the org host https://aicraftspeopleguild.github.io/.
   ═══════════════════════════════════════════════════════ */
'use strict';

function _detectBase() {
  const host = location.hostname;
  if (host === 'localhost' || host === '127.0.0.1') {
    return 'https://teslasolar.github.io/aicraftspeopleguild.github.io/guild/Enterprise/L4';
  }
  // If path contains a project-page prefix (/<repo>/...), keep it.
  const first = (location.pathname.split('/').filter(Boolean)[0]) || '';
  const prefix = first && first.endsWith('.github.io') ? `/${first}` : '';
  return `${location.origin}${prefix}/guild/Enterprise/L4`;
}

const BASE = _detectBase();

const ENDPOINTS = {
  health:  `${BASE}/api/health.json`,
  papers:  `${BASE}/api/papers.json`,
  members: `${BASE}/api/members.json`,
  state:   `${BASE}/api/state.json`,
  tags:    `${BASE}/runtime/tags.json`,
};
