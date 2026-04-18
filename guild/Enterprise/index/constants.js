// ── Timing ────────────────────────────────────────────────────────────
export const HEARTBEAT_MS = 5000;
export const REFRESH_MS   = 5000;
export const CLIENT_TTL   = 15000;
export const LS_TAB_KEY   = 'acg.ix.tab';

// ── Subsystem catalogue ───────────────────────────────────────────────
// Children render as a collapsible <details> group in the west dock.
// Every subsystem resolves to /{path}/ (trailing slash added by paintWest).
// Paths are written relative to the Enterprise root and organised by
// ISA-95 level (L1 plc · L2 scada/hmi · L3 db · L4 sandbox).
export const SUBSYSTEMS=[
  // L1
  {sub:'plc',     glyph:'🔧', name:'plc',     path:'L1/plc', children:[
    {sub:'forms.tag-write',     glyph:'🏷', name:'tag write',    path:'L1/forms/tag-write'},
    {sub:'forms.log-entry',     glyph:'⚠', name:'log entry',    path:'L1/forms/log-entry'},
    {sub:'forms.control-action',glyph:'🎛', name:'control action',path:'L1/forms/control-action'},
  ]},
  // L2
  {sub:'hmi',     glyph:'🖼', name:'hmi',     path:'L2/hmi'},
  {sub:'chat',    glyph:'💬', name:'chat',    path:'L2/hmi/chat'},
  {sub:'scada',   glyph:'🖥️', name:'scada',   path:'L2/scada', children:[
    {sub:'errors',  glyph:'⚠',  name:'errors',  path:'L2/scada/errors'},
    {sub:'alarms',  glyph:'🔔', name:'alarms',  path:'L2/scada/alarms'},
  ]},
  {sub:'state',   glyph:'📊', name:'state',   path:'L2/state'},
  {sub:'auth',    glyph:'🔑', name:'auth',    path:'L2/scada/gateway/auth', children:[
    {sub:'auth.webrtc',     glyph:'📡', name:'webrtc',     path:'L2/scada/gateway/auth/webrtc'},
    {sub:'auth.webtorrent', glyph:'🌊', name:'webtorrent', path:'L2/scada/gateway/auth/webtorrent'},
    {sub:'auth.discord',    glyph:'🎮', name:'discord',    path:'L2/scada/gateway/auth/discord'},
    {sub:'auth.github',     glyph:'🐙', name:'github',     path:'L2/scada/gateway/auth/github'},
    {sub:'auth.google',     glyph:'🔎', name:'google',     path:'L2/scada/gateway/auth/google'},
  ]},
  // L3
  {sub:'db',      glyph:'🗄️', name:'db',      path:'L3/db'},
  // L4
  {sub:'programs',glyph:'⚙', name:'programs', path:'L4/programs'},
  {sub:'api',     glyph:'🔌', name:'api',     path:'L4/api'},
  {sub:'sandbox', glyph:'🧪', name:'sandbox', path:'L4/sandbox'},
  // Cross-cutting
  {sub:'members', glyph:'👥', name:'members', path:'members'},
  {sub:'papers',  glyph:'📄', name:'papers',  path:'papers'},
  {sub:'mesh',    glyph:'🛰', name:'mesh',    path:'mesh'},
];

// ── Shell nav links ───────────────────────────────────────────────────
// hrefs are relative to the Enterprise root (prepended with basePath at render time).
export const SHELL_LINKS=[
  {href:'../apps/p2p/',                          label:'⚒ mesh'},
  {href:'L2/hmi/chat/',                          label:'💬 chat'},
  {href:'L2/state/',                             label:'📊 state'},
  {href:'L2/scada/alarms/',                      label:'🔔 alarms'},
  {href:'L2/scada/gateway/gateway-log.html',     label:'⚠ log'},
  {href:'L2/scada/gateway/health.html',          label:'⚕ health'},
  {href:'L4/api/',                               label:'🔌 api'},
  {href:'mesh/',                                 label:'🛰 topology'},
];
