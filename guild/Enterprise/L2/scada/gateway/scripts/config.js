// Every tracker in this list is dialled in parallel by p2p.js (not
// sequential fallback), so peers find each other via the union. Keep
// it short — most public WSS trackers have come and gone. Trim dead
// ones via /health.html.
export const TRACKERS=[
  'wss://tracker.openwebtorrent.com',
  'wss://tracker.webtorrent.dev',
];

export const ICE={iceServers:[
  {urls:'stun:stun.l.google.com:19302'},
  {urls:'stun:stun1.l.google.com:19302'},
  {urls:'stun:stun2.l.google.com:19302'},
]};

// Offers created per announce. Every offer = one RTCPeerConnection
// until a peer answers or PENDING_TTL_MS expires it (p2p.js). Chrome
// caps ~500 PCs per document; 5 offers × fan-out to every tracker,
// with one shared batch across trackers, keeps the steady-state pool
// at ~10 PCs.
export const N_OFFERS=5;

// 20 bytes exactly: '-ACG001-' (8) + 6 random bytes hex (12) = 20
export const myId='-ACG001-'+Array.from(crypto.getRandomValues(new Uint8Array(6))).map(b=>b.toString(16).padStart(2,'0')).join('');
export const myNm=myId.slice(-8);
export const myEm=['⚒️','🔨','🛠️','⚙️','🔧','📐','🧬','🛡️'][parseInt(myId.slice(-2),16)%8];

/* ═══ OAUTH (configure before use) ═══
 * Discord: implicit grant works purely in-browser. Set DISCORD.clientId
 *   and add this origin's URL to the app's OAuth redirects in the Discord
 *   dev portal (https://discord.com/developers/applications).
 * GitHub:  OAuth + device flow endpoints do NOT send CORS headers, so a
 *   tiny proxy is required. Set GITHUB.proxyUrl to a Cloudflare Worker (or
 *   any backend) that forwards POST /device/code and /access_token to
 *   github.com and relays the response. Leave proxyUrl empty to disable.
 */
export const OAUTH={
  DISCORD:{
    clientId:'',                                   // set me
    redirectUri:location.origin+location.pathname, // this page
    scope:'identify',
  },
  GITHUB:{
    clientId:'',   // set me (public OAuth app client id)
    proxyUrl:'',   // set me (e.g. https://acg-gh-proxy.workers.dev)
    scope:'read:user',
  },
};
