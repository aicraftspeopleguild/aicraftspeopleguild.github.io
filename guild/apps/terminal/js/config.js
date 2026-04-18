/* ═══════════════════════════════════════════════════════
   config.js — API base URL and endpoint map
   ═══════════════════════════════════════════════════════ */
'use strict';

const BASE = 'https://teslasolar.github.io/aicraftspeopleguild.github.io/guild/Enterprise/L4';

const ENDPOINTS = {
  health:  `${BASE}/api/health.json`,
  papers:  `${BASE}/api/papers.json`,
  members: `${BASE}/api/members.json`,
  state:   `${BASE}/api/state.json`,
  tags:    `${BASE}/runtime/tags.json`,
};
