// ═══ preview · live SVG viewer with auto-refresh ═══
import { log } from './log.js';

const SVG_DIR = '../../Enterprise/L2/hmi/web/assets/svg/';
// Fallback tab list — used if the dynamic SvgOrganism lookup fails.
const DEFAULT_TABS = [
  'scada-dashboard', 'heartbeat', 'tag-activity', 'tag-grid',
  'pipeline-pulse', 'fault-timeline', 'cmd-panel', 'scada-network',
  'commit-activity', 'tag-heatmap', 'architecture',
];

let currentSvg = 'scada-dashboard';
let tickId = null;

export function refreshSvg() {
  const frame = document.getElementById('svg-frame');
  if (frame) frame.src = SVG_DIR + currentSvg + '.svg?cb=' + Date.now();
}

export function switchTo(name) {
  currentSvg = name;
  document.querySelectorAll('.tab').forEach(x => x.classList.toggle('on', x.dataset.svg === name));
  const meta = document.getElementById('meta-left');
  if (meta) meta.textContent = name + '.svg';
  refreshSvg();
}

// Discover SvgOrganism ids. Tries the root tag.db indirectly by fetching
// the widget gallery SVG and scraping xlink-free links → not reliable.
// Instead: HEAD-probe DEFAULT_TABS and only keep the ones that exist.
async function discover() {
  const exists = async name => {
    try {
      const r = await fetch(SVG_DIR + name + '.svg', { method: 'HEAD' });
      return r.ok;
    } catch { return false; }
  };
  const found = [];
  for (const n of DEFAULT_TABS) if (await exists(n)) found.push(n);
  return found;
}

export async function bootPreview() {
  const host = document.getElementById('tabs');
  if (!host) return;
  host.innerHTML = '';
  const tabs = await discover();
  for (const name of tabs) {
    const b = document.createElement('button');
    b.className = 'tab' + (name === currentSvg ? ' on' : '');
    b.dataset.svg = name;
    b.textContent = name.replace(/-/g, ' ').slice(0, 18);
    b.addEventListener('click', () => switchTo(name));
    host.appendChild(b);
  }
  refreshSvg();
  if (tickId) clearInterval(tickId);
  tickId = setInterval(refreshSvg, 10000);
  log(`preview: ${tabs.length} tabs loaded · auto-refresh 10s`, 'ok');
}
