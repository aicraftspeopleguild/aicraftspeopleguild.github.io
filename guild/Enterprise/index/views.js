// ── Main-dock view painters + live-client bar ─────────────────────────

import {el,esc,fmtTs} from './dom.js';
import {LS_TAB_KEY,CLIENT_TTL} from './constants.js';

// ── Description ───────────────────────────────────────────────────────
export function paintDesc(host,desc){
  if(desc)host.append(el('p',{class:'ix-lede'},desc));
}

// ── UDTs pane ─────────────────────────────────────────────────────────
export function paintUdts(host,udts){
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

// ── Tags pane ─────────────────────────────────────────────────────────
function getLive(db,path){
  const parts=path.split('.');let x=db;
  for(const p of parts){if(x==null)return null;x=x[p]}
  return x&&x.value!==undefined?x:null;
}
function qDot(q){return({good:'🟢',stale:'🟡',bad:'🔴',uncertain:'⚪'})[q]||'⚪'}

export function paintTags(host,tags,liveDb){
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

// ── Tab bar + two panes ───────────────────────────────────────────────
// Returns {udtsHost, tagsHost, setTab}.
export function paintViews(host){
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

// ── Live clients bar ──────────────────────────────────────────────────
export const liveClients=new Map();

export function paintClientsBar(host){
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

// ── Footer feed ───────────────────────────────────────────────────────
export function setFooterFeed(env){
  const f=document.getElementById('dock-s-feed');if(!f)return;
  const v=typeof env.value==='object'?JSON.stringify(env.value):(env.value??'');
  f.textContent=`${fmtTs(env.ts)} · ${env.source}/${env.type}${env.path?' · '+env.path:''}${v?' · '+v:''}`;
}
