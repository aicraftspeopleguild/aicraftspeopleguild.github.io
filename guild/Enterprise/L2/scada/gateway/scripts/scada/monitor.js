// ═══ SCADA HMI · tag monitor drawer ═══
// A slide-in right-hand drawer that shows every tag in the registry with its
// value, quality and relative age. Writes publish → rAF-debounced re-render;
// 1Hz timer refreshes relative-age strings while open.

import * as tags from './tags.js';

let panel,tbody,filterIn,hidden=true,dirty=false,off=null;

function fmtAge(ts){
  const s=Math.floor((Date.now()-ts)/1000);
  if(s<1)return 'now';
  if(s<60)return s+'s';
  if(s<3600)return Math.floor(s/60)+'m';
  if(s<86400)return Math.floor(s/3600)+'h';
  return Math.floor(s/86400)+'d';
}

function fmtVal(v){
  if(v==null)return '—';
  if(typeof v==='number')return String(v);
  if(typeof v==='boolean')return v?'true':'false';
  if(typeof v==='string')return v;
  try{return JSON.stringify(v)}catch{return String(v)}
}

function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

function render(){
  const filter=filterIn.value.trim().toLowerCase();
  const rows=[];
  for(const[p,t]of tags.list()){
    if(filter&&!p.toLowerCase().includes(filter))continue;
    rows.push(
      `<tr class="q-${t.quality}"><td class="p">${esc(p)}</td>`+
      `<td class="v">${esc(fmtVal(t.value))}</td>`+
      `<td class="q">${t.quality}</td>`+
      `<td class="t">${t.type||''}</td>`+
      `<td class="a">${fmtAge(t.ts)}</td></tr>`
    );
  }
  tbody.innerHTML=rows.join('')||'<tr><td colspan="5" class="mt">no tags</td></tr>';
}

function schedule(){
  if(hidden||dirty)return;
  dirty=true;
  requestAnimationFrame(()=>{dirty=false;render()});
}

function mount(){
  panel=document.createElement('div');
  panel.id='scada';
  panel.innerHTML=`
    <div class="sc-hd">
      <span>⚙ SCADA · tag monitor</span>
      <input class="sc-f" id="sc-f" placeholder="filter… (e.g. tracker, peers.)" spellcheck="false">
      <button class="bt g" id="sc-x">×</button>
    </div>
    <div class="sc-wrap">
      <table class="sc-tbl">
        <thead><tr><th>Tag</th><th>Value</th><th>Q</th><th>Type</th><th>Age</th></tr></thead>
        <tbody id="sc-rows"></tbody>
      </table>
    </div>
    <div class="sc-ft" id="sc-ft">—</div>
  `;
  document.body.appendChild(panel);
  tbody=panel.querySelector('#sc-rows');
  filterIn=panel.querySelector('#sc-f');
  panel.querySelector('#sc-x').onclick=toggle;
  filterIn.oninput=schedule;
}

function updFooter(){
  const n=tags.list().length;
  panel.querySelector('#sc-ft').textContent=n+' tag'+(n===1?'':'s')+' · '+new Date().toLocaleTimeString();
}

export function toggle(){hidden?open():close()}

export function open(sync=true){
  hidden=false;panel.classList.add('open');
  if(!off)off=tags.subscribe('**',schedule);
  render();updFooter();
  if(sync&&!location.hash.startsWith('#scada'))history.replaceState(null,'','#scada');
}

export function close(sync=true){
  hidden=true;panel.classList.remove('open');
  if(off){off();off=null}
  if(sync&&location.hash.startsWith('#scada'))history.replaceState(null,'',location.pathname+location.search);
}

function applyHash(){
  const h=location.hash;
  if(h==='#scada'||h.startsWith('#scada?')||h.startsWith('#scada/')){
    // optional filter syntax: #scada?tracker  or  #scada/tracker
    const q=h.slice(6).replace(/^[?\/]/,'');
    open(false);
    if(q&&filterIn){filterIn.value=decodeURIComponent(q);render()}
  }else if(!hidden){
    close(false);
  }
}

export function startMonitor(){
  mount();
  setInterval(()=>{if(!hidden){render();updFooter()}},1000);
  window.addEventListener('hashchange',applyHash);
  applyHash();
}
