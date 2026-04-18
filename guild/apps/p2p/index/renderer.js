// ═══ ACG subsystem-index renderer ═══
// Each /{sub}/index.html calls renderSection({sub, glyph, name}).  The
// renderer paints a five-dock shell (north, west, main, east, south)
// identical across every subsystem.  The main dock splits into two
// tab views: 🏗️ UDTs and 🏷️ Tags.  Pages heartbeat every 5 s on
// BroadcastChannel "acg-mesh" so open siblings can see each other.

import {bridge} from '../../../Enterprise/L4/sandbox/shared/mesh-bridge.js';

// ── catalogues ────────────────────────────────────────────────────────
// Children render as a collapsible <details> group in the west dock.
// Every subsystem resolves to /{path}/ (trailing slash added by paintWest).
// Paths are written relative to the Enterprise root and organised by
// ISA-95 level (L1 plc · L2 scada/hmi · L3 db · L4 sandbox).
export const SUBSYSTEMS=[
  {sub:'chat',    glyph:'💬', name:'chat',    path:'L2/hmi/chat'},
  {sub:'scada',   glyph:'🖥️', name:'scada',   path:'L2/scada', children:[
    {sub:'errors',  glyph:'⚠',  name:'errors',  path:'L2/scada/errors'},
  ]},
  {sub:'auth',    glyph:'🔑', name:'auth',    path:'L2/scada/gateway/auth', children:[
    {sub:'auth.webrtc',     glyph:'📡', name:'webrtc',     path:'L2/scada/gateway/auth/webrtc'},
    {sub:'auth.webtorrent', glyph:'🌊', name:'webtorrent', path:'L2/scada/gateway/auth/webtorrent'},
    {sub:'auth.discord',    glyph:'🎮', name:'discord',    path:'L2/scada/gateway/auth/discord'},
    {sub:'auth.github',     glyph:'🐙', name:'github',     path:'L2/scada/gateway/auth/github'},
    {sub:'auth.google',     glyph:'🔎', name:'google',     path:'L2/scada/gateway/auth/google'},
  ]},
  {sub:'hmi',     glyph:'🖼', name:'hmi',     path:'L2/hmi'},
  {sub:'plc',     glyph:'🔧', name:'plc',     path:'L1/plc'},
  {sub:'db',      glyph:'🗄️', name:'db',      path:'L3/db'},
  {sub:'sandbox', glyph:'🧪', name:'sandbox', path:'L4/sandbox'},
];

const SHELL_LINKS=[
  {href:'../apps/p2p/',                          label:'⚒ mesh'},
  {href:'L2/hmi/chat/',                          label:'💬 chat'},
  {href:'L2/scada/gateway/gateway-log.html',     label:'⚠ log'},
  {href:'L2/scada/gateway/health.html',          label:'⚕ health'},
];

const HEARTBEAT_MS = 5000;
const REFRESH_MS   = 5000;
const CLIENT_TTL   = 15000;
const LS_TAB_KEY   = 'acg.ix.tab';

// ── utilities ────────────────────────────────────────────────────────
const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const fmtTs=ts=>ts?new Date(ts).toLocaleTimeString():'—';

async function fetchJson(url){
  const r=await fetch(url,{cache:'no-store'});
  if(!r.ok)throw new Error(url+' → HTTP '+r.status);
  return r.json();
}

function el(tag,attrs={},children=[]){
  const node=document.createElement(tag);
  for(const[k,v]of Object.entries(attrs)){
    if(k==='class')node.className=v;
    else if(k==='html')node.innerHTML=v;
    else node.setAttribute(k,v);
  }
  for(const c of[].concat(children||[]))if(c!=null)node.append(c.nodeType?c:document.createTextNode(c));
  return node;
}

// ── NESW dock shell ──────────────────────────────────────────────────
export function buildDockShell(root){
  root.innerHTML='';
  root.className='dock-shell';
  const docks={
    n: el('header',{class:'dock-n'}),
    w: el('aside', {class:'dock-w'}),
    m: el('section',{class:'dock-m'}),
    e: el('aside', {class:'dock-e'}),
    s: el('footer',{class:'dock-s'}),
  };
  root.append(docks.n,docks.w,docks.m,docks.e,docks.s);
  return docks;
}

export {paintNorth, paintWest, paintEast, paintSouth, SHELL_LINKS};
function paintNorth(host,{glyph,name,basePath}){
  host.append(el('div',{class:'dock-n-logo'},[glyph+' '+name, el('span',{},' · ACG subsystem')]));
  const shell=el('nav',{class:'dock-n-shell'},
    SHELL_LINKS.map(l=>el('a',{href:basePath+l.href},l.label))
  );
  host.append(shell);
}

// ── west dock: subsystem nav with collapsible children ───────────────
// Each SUBSYSTEMS entry renders as either:
//   - flat <a> row (no children), or
//   - <details> dropdown whose <summary> is the parent anchor and whose
//     body lists the children (one <a> each, visually indented).
// The current subsystem is marked `.on`; if the current subsystem is a
// child, its parent group is also opened by default.
function navAnchor({sub,glyph,name,path},{activeSub,basePath,indent}){
  const a=el('a',{
    class:(sub===activeSub?'on':'')+(indent?' dock-w-sub':''),
    href:basePath+path+'/',
  },[glyph+' '+name]);
  return a;
}

function paintWest(host,{sub:activeSub,basePath}){
  host.append(el('h4',{},'Subsystems'));
  const nav=el('nav',{class:'dock-w-nav'});

  for(const s of SUBSYSTEMS){
    if(!s.children||!s.children.length){
      nav.append(navAnchor(s,{activeSub,basePath,indent:false}));
      continue;
    }
    const childActive=s.children.some(c=>c.sub===activeSub);
    const parentActive=s.sub===activeSub;
    const open=childActive||parentActive;

    const details=el('details',{class:'dock-w-group'+(open?' open':'')});
    if(open)details.setAttribute('open','');

    const summary=el('summary',{class:'dock-w-summary'+(parentActive?' on':'')},
      [s.glyph+' '+s.name]
    );
    details.append(summary);

    // Parent page link (clicking the caret toggles; clicking text here
    // navigates — we put it as the first child under the summary)
    const parentLink=el('a',{
      class:'dock-w-parent-link'+(parentActive?' on':''),
      href:basePath+s.path+'/',
    },['open '+s.name+' overview']);
    const kids=el('div',{class:'dock-w-subs'});
    kids.append(parentLink);
    for(const c of s.children){
      kids.append(navAnchor(c,{activeSub,basePath,indent:true}));
    }
    details.append(kids);
    nav.append(details);
  }
  host.append(nav);

  host.append(el('hr',{class:'dock-sep'}));
  host.append(el('h4',{},'Controls'));
  host.append(el('div',{class:'dock-w-actions'},[
    el('a',{href:basePath+'.github/ISSUE_TEMPLATE/tag-update.yml'},'🏷️ write tag'),
    el('a',{href:basePath+'.github/ISSUE_TEMPLATE/log-entry.yml'},'⚠ log incident'),
    el('a',{href:basePath+'.github/ISSUE_TEMPLATE/control-action.yml'},'🎛 control action'),
  ]));
}

// ── main dock: description + tabbed UDTs / Tags views ────────────────
function paintDesc(host,desc){
  if(desc)host.append(el('p',{class:'ix-lede'},desc));
}

function paintUdts(host,udts){
  host.innerHTML='';
  const sec=el('section',{class:'ix-sec'});
  sec.append(el('h2',{},'🏗️ UDTs'));
  if(!udts||!udts.types||!Object.keys(udts.types).length){
    sec.append(el('p',{class:'ix-muted'},'no UDTs declared'));
    host.append(sec);return;
  }
  for(const[name,def]of Object.entries(udts.types)){
    const card=el('div',{class:'ix-card'});
    card.append(el('h3',{},[def.glyph?def.glyph+' ':'',name]));
    if(def.desc)card.append(el('p',{class:'ix-muted'},def.desc));
    const tbl=el('table',{class:'ix-tbl'});
    tbl.append(el('thead',{html:'<tr><th>field</th><th>type</th></tr>'}));
    const tb=el('tbody');
    const fields=Array.isArray(def.fields)?def.fields.map(f=>[f,'any']):Object.entries(def.fields||{});
    for(const[f,t]of fields){
      tb.append(el('tr',{html:`<td>${esc(f)}</td><td><code>${esc(t)}</code></td>`}));
    }
    tbl.append(tb);card.append(tbl);sec.append(card);
  }
  host.append(sec);
}

function getLive(db,path){
  const parts=path.split('.');let x=db;
  for(const p of parts){if(x==null)return null;x=x[p]}
  return x&&x.value!==undefined?x:null;
}
function qDot(q){return({good:'🟢',stale:'🟡',bad:'🔴',uncertain:'⚪'})[q]||'⚪'}

function paintTags(host,tags,liveDb){
  host.innerHTML='';
  const sec=el('section',{class:'ix-sec'});
  sec.append(el('h2',{},'🏷️ Tags'));
  if(!tags||!tags.tags||!tags.tags.length){
    sec.append(el('p',{class:'ix-muted'},'no tags declared'));
    host.append(sec);return;
  }
  const tbl=el('table',{class:'ix-tbl'});
  tbl.append(el('thead',{html:'<tr><th>path</th><th>type</th><th>value</th><th>quality</th><th>updated</th></tr>'}));
  const tb=el('tbody');
  for(const t of tags.tags){
    const path=t.path||t.pathPattern||'?';
    const live=t.path?getLive(liveDb||{},t.path):null;
    const val=live?(typeof live.value==='object'?JSON.stringify(live.value):String(live.value)):(t.cardinality==='many'?'<pattern>':'—');
    const quality=live?live.quality:(t.cardinality==='many'?'—':'uncertain');
    const updated=live?fmtTs(live.ts):'—';
    tb.append(el('tr',{html:
      `<td><code>${esc(path)}</code></td>`+
      `<td>${esc(t.type||'')}</td>`+
      `<td class="ix-v">${esc(val)}</td>`+
      `<td>${qDot(quality)} ${esc(quality)}</td>`+
      `<td class="ix-muted">${esc(updated)}</td>`
    }));
  }
  tbl.append(tb);sec.append(tbl);
  if(tags.namespaces)sec.append(el('p',{class:'ix-muted'},'namespaces: '+tags.namespaces.join(', ')));
  host.append(sec);
}

// Build the tab bar + two panes; return {udtsHost, tagsHost, setTab}.
function paintViews(host){
  const tabs=el('nav',{class:'ix-tabs'});
  const tabUdts=el('button',{class:'ix-tab',type:'button','data-view':'udts'},'🏗️ UDTs');
  const tabTags=el('button',{class:'ix-tab',type:'button','data-view':'tags'},'🏷️ Tags');
  tabs.append(tabUdts,tabTags);
  host.append(tabs);

  const udtsHost=el('div',{class:'ix-pane','data-view':'udts'});
  const tagsHost=el('div',{class:'ix-pane','data-view':'tags'});
  host.append(udtsHost,tagsHost);

  function setTab(name){
    const t=(name==='tags'?'tags':'udts');
    tabUdts.classList.toggle('on',t==='udts');
    tabTags.classList.toggle('on',t==='tags');
    udtsHost.hidden=(t!=='udts');
    tagsHost.hidden=(t!=='tags');
    try{localStorage.setItem(LS_TAB_KEY,t)}catch(e){}
  }
  tabUdts.addEventListener('click',()=>setTab('udts'));
  tabTags.addEventListener('click',()=>setTab('tags'));

  const saved=(()=>{try{return localStorage.getItem(LS_TAB_KEY)}catch(e){return null}})();
  setTab(saved||'udts');

  return{udtsHost,tagsHost,setTab};
}

// ── east dock: live clients + broadcast ──────────────────────────────
function paintEast(host,{sub}){
  const clientsSec=el('section',{class:'dock-e-sec'},[
    el('h3',{},'💓 Live clients'),
    el('div',{id:'dock-e-clients',class:'ix-hbrow'}),
  ]);
  host.append(clientsSec);

  const castSec=el('section',{class:'dock-e-sec'},[el('h3',{},'📣 Broadcast')]);
  const row=el('div',{class:'ix-row'});
  const input=el('input',{class:'ix-in',placeholder:'ping sibling tabs…'});
  const btn=el('button',{class:'ix-btn'},'send');
  btn.addEventListener('click',()=>{
    const v=input.value.trim()||'ping';
    bridge.publish(sub,'ping',{path:'broadcast',value:v});
    input.value='';
  });
  input.addEventListener('keydown',e=>{if(e.key==='Enter')btn.click()});
  row.append(input,btn);
  castSec.append(row);
  host.append(castSec);

  const cadSec=el('section',{class:'dock-e-sec'},[
    el('h3',{},'⏱ Cadence'),
    el('p',{class:'ix-muted'},'heartbeat 5 s · tag refresh 5 s · commit poll 90 s'),
  ]);
  host.append(cadSec);
}

// ── south dock: rolling mesh feed ────────────────────────────────────
function paintSouth(host){
  host.append(el('span',{class:'dock-s-mark'},'⚒ AI Craftspeople Guild · P2P'));
  host.append(el('span',{class:'dock-s-feed',id:'dock-s-feed'},'— idle —'));
  host.append(el('span',{class:'dock-s-cadence',id:'dock-s-cadence'},'💓 5s'));
}

// ── live wiring: heartbeats + bus subscribe ──────────────────────────
const liveClients=new Map();

function paintClientsBar(host){
  if(!host)return;
  const now=Date.now();
  const alive=[...liveClients.entries()].filter(([,v])=>now-v.ts<CLIENT_TTL).sort((a,b)=>a[0].localeCompare(b[0]));
  host.innerHTML=alive.length
    ?alive.map(([src,v])=>{
        const age=Math.floor((now-v.ts)/1000);
        return `<span class="ix-hbpill" title="last heartbeat ${age}s ago · ${v.path||''}">${esc(src)} · ${age}s</span>`;
      }).join('')
    :'<span class="ix-muted">no sibling pages in last 15 s</span>';
}

function setFooterFeed(env){
  const f=document.getElementById('dock-s-feed');if(!f)return;
  const v=typeof env.value==='object'?JSON.stringify(env.value):(env.value??'');
  f.textContent=`${fmtTs(env.ts)} · ${env.source}/${env.type}${env.path?' · '+env.path:''}${v?' · '+v:''}`;
}

// ── entry ────────────────────────────────────────────────────────────
export async function renderSection(opts){
  const{sub,glyph,name,desc}=opts;
  const basePath=opts.basePath||'../';
  const root=document.getElementById('section')||document.body;

  const docks=buildDockShell(root);
  paintNorth(docks.n,{glyph,name,basePath});
  paintWest(docks.w,{sub,basePath});
  paintEast(docks.e,{sub});
  paintSouth(docks.s);

  paintDesc(docks.m,desc);
  const{udtsHost,tagsHost}=paintViews(docks.m);

  const udtsP=fetchJson(opts.udtsPath||'./udts.json').catch(()=>null);
  const tagsP=fetchJson(opts.tagsPath||'./tags.json').catch(()=>null);
  const dbPath=opts.dbPath||basePath+'controls/db/tags.json';
  let db=await fetchJson(dbPath).catch(()=>null);
  const [udts,tags]=await Promise.all([udtsP,tagsP]);

  paintUdts(udtsHost,udts);
  paintTags(tagsHost,tags,db);

  // bus: heartbeats → live clients, every envelope → footer ticker
  const clientsHost=document.getElementById('dock-e-clients');
  bridge.subscribe(env=>{
    if(env.type==='heartbeat'&&env.source){
      liveClients.set(env.source,{ts:env.ts||Date.now(),path:env.path||''});
    }
    setFooterFeed(env);
  });
  paintClientsBar(clientsHost);

  // heartbeat + repaint cadences
  function beat(){bridge.publish(sub,'heartbeat',{path:location.pathname,value:{href:location.href}})}
  bridge.publish(sub,'page-open',{path:location.pathname,value:{href:location.href}});
  beat();setInterval(beat,HEARTBEAT_MS);
  setInterval(()=>paintClientsBar(clientsHost),1000);

  // tag table auto-refresh
  setInterval(async()=>{
    try{
      db=await fetchJson(dbPath+'?t='+Date.now());
      paintTags(tagsHost,tags,db);
    }catch(e){}
  },REFRESH_MS);

  window.addEventListener('beforeunload',()=>{
    bridge.publish(sub,'page-close',{path:location.pathname});
  });
}
