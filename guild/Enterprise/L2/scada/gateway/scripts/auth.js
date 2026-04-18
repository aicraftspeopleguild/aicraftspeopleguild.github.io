import {$,esc,log} from './ui.js';
import {OAUTH,myId,myNm,myEm} from './config.js';
import {AUTH} from './scada/providers.js';
import {mkUDT} from './scada/udt.js';
import * as tags from './scada/tags.js';

const KEY='acg.profile';
const listeners=new Set();
let profile=load();
publishProfile();

function load(){
  try{return JSON.parse(localStorage.getItem(KEY)||'null')}catch{return null}
}
function save(p){
  profile=p;
  if(p)localStorage.setItem(KEY,JSON.stringify(p));
  else localStorage.removeItem(KEY);
  publishProfile();
  listeners.forEach(f=>{try{f(profile)}catch(e){}});
  paint();
}

function publishProfile(){
  if(profile)AUTH.write('profile',mkUDT('Profile',profile));
  else AUTH.del('profile');
  AUTH.write('signedIn',!!profile);
}

export function getProfile(){return profile}
export function onProfileChange(fn){listeners.add(fn);return()=>listeners.delete(fn)}
export function logout(){save(null);log('signed out','wr')}

/* ═══ DISCORD · implicit grant (pure browser) ═══ */
function discordLogin(){
  const {clientId,redirectUri,scope}=OAUTH.DISCORD;
  if(!clientId){log('discord clientId not configured','er');return}
  const state=crypto.randomUUID();
  sessionStorage.setItem('acg.oauth.state',state);
  sessionStorage.setItem('acg.oauth.provider','discord');
  const u=new URL('https://discord.com/oauth2/authorize');
  u.searchParams.set('client_id',clientId);
  u.searchParams.set('redirect_uri',redirectUri);
  u.searchParams.set('response_type','token');
  u.searchParams.set('scope',scope);
  u.searchParams.set('state',state);
  location.href=u.toString();
}

async function discordFinish(token){
  const r=await fetch('https://discord.com/api/users/@me',{headers:{Authorization:'Bearer '+token}});
  if(!r.ok)throw new Error('discord /users/@me '+r.status);
  const u=await r.json();
  const avatar=u.avatar
    ?`https://cdn.discordapp.com/avatars/${u.id}/${u.avatar}.png?size=64`
    :`https://cdn.discordapp.com/embed/avatars/${(parseInt(u.id)>>22)%6}.png`;
  save({provider:'discord',id:u.id,username:u.global_name||u.username,avatar});
  log('✓ signed in as '+(u.global_name||u.username)+' (discord)','ok');
}

/* ═══ GITHUB · device flow via CORS proxy ═══
 * Proxy contract (HTTPS POST, JSON in/out):
 *   POST {proxyUrl}/device/code
 *     body: {client_id, scope}  →  forwards to github.com/login/device/code
 *   POST {proxyUrl}/access_token
 *     body: {client_id, device_code, grant_type}
 *                              →  forwards to github.com/login/oauth/access_token
 * The proxy just sets CORS headers + Accept:application/json; it holds no secret.
 */
async function githubLogin(){
  const {clientId,proxyUrl,scope}=OAUTH.GITHUB;
  if(!clientId||!proxyUrl){
    log('github login: clientId or proxyUrl not configured','er');
    alert('GitHub login requires OAUTH.GITHUB.clientId and proxyUrl (see js/config.js)');
    return;
  }
  log('github: requesting device code…','hi');
  let dc;
  try{
    const r=await fetch(proxyUrl.replace(/\/$/,'')+'/device/code',{
      method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},
      body:JSON.stringify({client_id:clientId,scope}),
    });
    if(!r.ok)throw new Error('HTTP '+r.status);
    dc=await r.json();
  }catch(e){log('github device code failed: '+e.message,'er');return}

  // user completes auth on github.com
  window.open(dc.verification_uri,'_blank','noopener');
  prompt('Enter this code on GitHub → '+dc.verification_uri,dc.user_code);

  // poll for token
  const interval=(dc.interval||5)*1000,deadline=Date.now()+dc.expires_in*1000;
  while(Date.now()<deadline){
    await new Promise(r=>setTimeout(r,interval));
    try{
      const r=await fetch(proxyUrl.replace(/\/$/,'')+'/access_token',{
        method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},
        body:JSON.stringify({client_id:clientId,device_code:dc.device_code,grant_type:'urn:ietf:params:oauth:grant-type:device_code'}),
      });
      const j=await r.json();
      if(j.error==='authorization_pending')continue;
      if(j.error==='slow_down'){await new Promise(r=>setTimeout(r,5000));continue}
      if(j.error){log('github: '+j.error,'er');return}
      if(j.access_token){await githubFinish(j.access_token);return}
    }catch(e){log('github poll err: '+e.message,'er')}
  }
  log('github device flow timed out','er');
}

async function githubFinish(token){
  const r=await fetch('https://api.github.com/user',{headers:{Authorization:'token '+token,Accept:'application/vnd.github+json'}});
  if(!r.ok)throw new Error('github /user '+r.status);
  const u=await r.json();
  save({provider:'github',id:String(u.id),username:u.login,avatar:u.avatar_url});
  log('✓ signed in as '+u.login+' (github)','ok');
}

/* ═══ REDIRECT HANDLER (call once on load) ═══ */
async function handleRedirect(){
  // discord: #access_token in fragment
  if(location.hash.includes('access_token=')){
    const p=new URLSearchParams(location.hash.slice(1));
    const tok=p.get('access_token'),state=p.get('state');
    const expected=sessionStorage.getItem('acg.oauth.state');
    const provider=sessionStorage.getItem('acg.oauth.provider');
    sessionStorage.removeItem('acg.oauth.state');
    sessionStorage.removeItem('acg.oauth.provider');
    history.replaceState(null,'',location.pathname+location.search);
    if(!tok||state!==expected){log('oauth state mismatch','er');return}
    try{
      if(provider==='discord')await discordFinish(tok);
    }catch(e){log('oauth finish failed: '+e.message,'er')}
  }
}

/* ═══ UI — consolidated auth dropdown ═══
 * Renders a single <details> pill with every auth sub-provider:
 *   📡 webrtc    — operator peer-id (always on; auto-login)
 *   🌊 webtorrent — tracker state (live from tracker.* tags)
 *   🎮 discord   — OAuth (signed in → chip + sign-out; else Sign in)
 *   🐙 github    — OAuth (same)
 *   🔎 google    — OIDC stub
 * The open/closed state is preserved across repaints.
 */
function trackerPill(){
  const st=(tags.read('tracker.state')||{}).value||'offline';
  const cls=st==='connected'?'ok':st==='offline'||st==='failed'?'err':'wrn';
  return{st,cls};
}
function trackerUrl(){
  return(tags.read('tracker.current')||{}).value?.url||'—';
}
function trackerSummary(){
  const cur=(tags.read('tracker.current')||{}).value||{};
  const n=(tags.read('tracker.count')||{}).value||0;
  const total=cur.configuredCount||0;
  if(!n)return 'no tracker open';
  const primary=cur.url?cur.url.split('/')[2]:'';
  return n+'/'+total+' trackers · primary <code>'+esc(primary)+'</code>';
}

function authRow({provider,glyph,title,status,action}){
  return `<div class="auth-row" data-provider="${esc(provider)}">
    <span class="auth-ic">${glyph}</span>
    <span class="auth-lb"><strong>${esc(title)}</strong><div class="auth-st">${status}</div></span>
    <span class="auth-ac">${action||''}</span>
  </div>`;
}

function oauthRow(provider,glyph,title,loginAction){
  const me=profile&&profile.provider===provider?profile:null;
  if(me){
    return authRow({
      provider,glyph,title,
      status:`signed in as <code>${esc(me.username)}</code>`,
      action:`<button class="auth-btn" data-action="logout">Sign out</button>`,
    });
  }
  return authRow({
    provider,glyph,title,
    status:'not signed in',
    action:`<button class="auth-btn" data-action="login-${esc(loginAction)}">Sign in</button>`,
  });
}

function paint(){
  const host=$('auth');if(!host)return;

  // preserve the dropdown open state
  const prev=host.querySelector('.auth-drop');
  const wasOpen=prev?prev.hasAttribute('open'):false;

  const t=trackerPill();
  const trackUrl=trackerUrl();
  const hasUser=!!profile;

  // summary: avatar + user name if signed in, else emoji + operator id
  const sumInner=hasUser
    ?`<img src="${esc(profile.avatar)}" alt=""><span>${esc(profile.username)}</span>`
    :`<span class="auth-em">${esc(myEm)}</span><span>operator · <code style="font-family:var(--ff-mono)">${esc(myNm)}</code></span>`;

  host.innerHTML=`
<details class="auth-drop"${wasOpen?' open':''}>
  <summary class="auth-sum">${sumInner}<span class="auth-caret">▾</span></summary>
  <div class="auth-body">
    ${authRow({
      provider:'webrtc',glyph:'📡',title:'WebRTC',
      status:`operator peer-id · <code>${esc(myId)}</code>`,
      action:`<span class="auth-pill ok">logged in</span>`,
    })}
    ${authRow({
      provider:'webtorrent',glyph:'🌊',title:'WebTorrent',
      status:trackerSummary(),
      action:`<span class="auth-pill ${t.cls}">${esc(t.st)}</span>`,
    })}
    <div class="auth-hr"></div>
    ${oauthRow('discord','🎮','Discord','discord')}
    ${oauthRow('github','🐙','GitHub','github')}
    ${authRow({
      provider:'google',glyph:'🔎',title:'Google',
      status:'OIDC implicit · not wired yet',
      action:`<span class="auth-pill muted">stub</span>`,
    })}
  </div>
</details>`;

  // wire click handlers
  host.querySelector('[data-action="login-discord"]')?.addEventListener('click',discordLogin);
  host.querySelector('[data-action="login-github"]')?.addEventListener('click',githubLogin);
  host.querySelectorAll('[data-action="logout"]').forEach(b=>b.addEventListener('click',logout));
}

// Live repaint when tracker state or count flips (webtorrent row)
tags.subscribe('tracker.state',paint);
tags.subscribe('tracker.current',paint);
tags.subscribe('tracker.count',paint);

export function startAuth(){
  paint();
  handleRedirect();
}
