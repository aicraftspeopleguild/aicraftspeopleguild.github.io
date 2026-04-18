// ═══ log · tiny line-logger into the on-screen log pane ═══
const pane = () => document.getElementById('log');

export function log(msg, cls = 'info') {
  const d = document.createElement('div');
  d.className = cls;
  d.textContent = new Date().toISOString().slice(11, 19) + '  ' + msg;
  const p = pane();
  if (p) p.prepend(d);
  else console.log('[cd]', msg);
}
