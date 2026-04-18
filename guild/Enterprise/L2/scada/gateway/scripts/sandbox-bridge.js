// ═══ Sandbox ↔ ACG bridge (main side) ═══
// Subscribes to BroadcastChannel("acg-mesh") and folds each envelope into
// the SCADA tag plant. Canonical envelope (§4):
//   { source, type, path?, value?, ts, … }
//
// Routing:
//   type === "tag"  →  sandbox.<source>.<path>  (mirrors the sandbox's
//                       internal tag path verbatim; preserves quality + udt)
//   else            →  sandbox.<source>.event.<type>  (full envelope as
//                       value) + increments sandbox.<source>.events.<type>.count

import * as tags from './scada/tags.js';

const CHAN='acg-mesh';
let ch=null;

function onEnvelope(env){
  if(!env||!env.source||!env.type)return;
  const base=`sandbox.${env.source}`;
  tags.write(base+'.lastEventAt',env.ts||Date.now(),{type:'DateTime'});
  tags.write(base+'.lastEvent',env.type);

  if(env.type==='tag'&&env.path){
    tags.write(`${base}.${env.path}`,env.value,{type:env.udt||null,quality:env.quality||'good'});
  }else{
    tags.write(`${base}.event.${env.type}`,env);
    tags.inc(`${base}.events.${env.type}.count`);
  }
}

export function startSandboxBridge(){
  try{ch=new BroadcastChannel(CHAN)}catch(e){return}
  ch.addEventListener('message',e=>onEnvelope(e.data));
  tags.write('sandbox.bridgeOpen',true);
  tags.write('sandbox.channel',CHAN);
}

export function stopSandboxBridge(){
  if(!ch)return;
  ch.close();ch=null;
  tags.write('sandbox.bridgeOpen',false);
}
