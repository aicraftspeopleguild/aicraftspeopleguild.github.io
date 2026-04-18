// ═══ Error wrapper (Gateway-log style) ═══
// Captures every error / warn / info from the app, maintains a ring buffer,
// persists to localStorage, publishes to the SCADA tag plant, and piggybacks
// off the acg-mesh BroadcastChannel so sandbox-page errors are visible too.
//
// Shape of a log entry:
//   { ts:ms, level:"ERROR"|"WARN"|"INFO"|"DEBUG", logger:s, msg:s, stack?:s, meta?:o }
//
// Tags published:
//   errors.count            counter
//   errors.byLevel.<L>.count
//   errors.last             last LogEntry
//   errors.ring             most recent N entries (JSON)

import * as tags from './scada/tags.js';

const KEY='acg.errors';
const CHAN='acg-mesh';
const N=200;                 // ring size
const ring=[];               // [{ts,level,logger,msg,stack?,meta?}]
let bridge=null;

function save(){
  try{localStorage.setItem(KEY,JSON.stringify(ring.slice(-N)))}catch(e){}
}

function load(){
  try{
    const arr=JSON.parse(localStorage.getItem(KEY)||'[]');
    if(Array.isArray(arr))ring.push(...arr.slice(-N));
  }catch(e){}
}

function publish(entry){
  tags.inc('errors.count');
  tags.inc(`errors.byLevel.${entry.level}.count`);
  tags.write('errors.last',entry);
  tags.write('errors.ring',ring.slice(-N));
  tags.write('errors.lastAt',entry.ts,{type:'DateTime'});
}

export function logEntry(level,logger,msg,meta){
  const entry={ts:Date.now(),level,logger:String(logger||'app'),msg:String(msg)};
  if(meta?.stack)entry.stack=meta.stack;
  if(meta&&(meta.stack?Object.keys(meta).length>1:true)){
    const{stack,...rest}=meta;if(Object.keys(rest).length)entry.meta=rest;
  }
  ring.push(entry);
  while(ring.length>N)ring.shift();
  save();publish(entry);
  // relay via mesh so other tabs / sandbox pages see it
  if(bridge){try{bridge.postMessage({source:'errors',type:'entry',value:entry,ts:entry.ts})}catch(e){}}
  return entry;
}

export const log={
  error:(logger,msg,meta)=>logEntry('ERROR',logger,msg,meta),
  warn: (logger,msg,meta)=>logEntry('WARN', logger,msg,meta),
  info: (logger,msg,meta)=>logEntry('INFO', logger,msg,meta),
  debug:(logger,msg,meta)=>logEntry('DEBUG',logger,msg,meta),
};

export function getAll(){return ring.slice()}
export function clearAll(){ring.length=0;save();tags.write('errors.ring',[]);tags.write('errors.count',0)}

export function exportJSON(){
  const payload={exportedAt:Date.now(),count:ring.length,entries:ring.slice()};
  return JSON.stringify(payload,null,2);
}

// Capture browser-level failures
function wireGlobalCapture(){
  window.addEventListener('error',(e)=>{
    logEntry('ERROR','window',e.message||'error',{stack:e.error?.stack,source:e.filename,line:e.lineno});
  });
  window.addEventListener('unhandledrejection',(e)=>{
    const r=e.reason;
    logEntry('ERROR','promise',r?.message||String(r),{stack:r?.stack});
  });
  // Wrap console.error to mirror into the log (keep original behaviour)
  const ce=console.error.bind(console);
  console.error=(...a)=>{
    try{logEntry('ERROR','console',a.map(String).join(' '))}catch(_){}
    ce(...a);
  };
  const cw=console.warn.bind(console);
  console.warn=(...a)=>{
    try{logEntry('WARN','console',a.map(String).join(' '))}catch(_){}
    cw(...a);
  };
}

function wireBridge(){
  try{bridge=new BroadcastChannel(CHAN)}catch(e){return}
  bridge.addEventListener('message',(e)=>{
    const env=e?.data;
    if(env?.source==='errors'&&env.type==='entry'&&env.value){
      // Foreign entry (from another tab / sandbox) — re-ingest without re-relaying
      const entry=env.value;
      ring.push(entry);while(ring.length>N)ring.shift();
      save();
      tags.inc('errors.count');
      tags.inc(`errors.byLevel.${entry.level}.count`);
      tags.write('errors.last',entry);
      tags.write('errors.ring',ring.slice(-N));
    }
  });
}

export function startErrorCapture(){
  load();
  wireBridge();
  wireGlobalCapture();
  tags.write('errors.count',ring.length,{type:'Counter'});
  tags.write('errors.ring',ring.slice(-N));
  log.info('errors','capture started',{ringSize:N});
}
