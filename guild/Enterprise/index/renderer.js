// ═══ ACG Enterprise renderer — barrel export ═════════════════════════
// Canonical location: guild/Enterprise/index/renderer.js
//
// All Enterprise subsystem pages import from a relative path that
// resolves here (e.g. ../../index/renderer.js from L2/scada/).
// The p2p shim at guild/apps/p2p/index/renderer.js re-exports from here
// so pages under guild/apps/p2p/ continue to work unchanged.

export {el,esc,fmtTs}                                         from './dom.js';
export {SUBSYSTEMS,SHELL_LINKS,
        HEARTBEAT_MS,REFRESH_MS,CLIENT_TTL,LS_TAB_KEY}        from './constants.js';
export {buildDockShell,paintNorth,paintWest,paintEast,paintSouth} from './shell.js';
export {paintDesc,paintUdts,paintTags,paintViews,
        paintClientsBar,liveClients,setFooterFeed}             from './views.js';
export {renderSection}                                         from './section.js';
