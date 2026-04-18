// ── renderSection — entry point for every subsystem page ─────────────

import {bridge}     from '../L4/sandbox/shared/mesh-bridge.js';
import {buildDockShell,paintNorth,paintWest,paintEast,paintSouth} from './shell.js';
import {paintDesc,paintUdts,paintTags,paintViews,paintClientsBar,liveClients,setFooterFeed} from './views.js';
import {HEARTBEAT_MS,REFRESH_MS} from './constants.js';

async function fetchJson(url){
  const r=await fetch(url,{cache:'no-store'});
  if(!r.ok)throw new Error(url+' → HTTP '+r.status);
  return r.json();
}

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
  const[udts,tags]=await Promise.all([udtsP,tagsP]);

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
