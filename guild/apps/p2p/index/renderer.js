// ═══ Backward-compat shim ════════════════════════════════════════════
// Canonical implementation moved to guild/Enterprise/index/.
// Pages under guild/apps/p2p/… import from ./renderer.js or
// ../index/renderer.js and continue to resolve here.
export * from '../../../Enterprise/index/renderer.js';
