// ═══ ACG Sandbox ↔ mesh bridge ═══
// Canonical channel: BroadcastChannel("acg-mesh").
// Canonical envelope (§4): { source:s type:s path:s value:any ts:ms … }
//
//   source  — owning tool name ("web-llm", …)
//   type    — "tag" for scada-tag relays; otherwise event name ("init",
//             "tool_call", "file_change", …)
//   path    — tag path or event sub-path (optional)
//   value   — tag value or event payload (optional)
//   ts      — epoch ms
//
// Usage (sandbox side):
//   bridge.publish('web-llm','tag',{path:'engine.ready',value:true,quality:'good',udt:null});
//   bridge.publish('web-llm','tool_call',{path:'create_file',value:{ok:true,path:'/x'}});
//
// Usage (main ACG side):
//   bridge.subscribe(env => { ... });

const CHAN='acg-mesh';

function openChannel(){
  try{return new BroadcastChannel(CHAN)}
  catch(e){return null}
}
const ch=openChannel();

export const bridge={
  channel:CHAN,
  publish(source,type,extra={}){
    const env={source,type,ts:Date.now(),...extra};
    if(ch)try{ch.postMessage(env)}catch(e){}
    return env;
  },
  subscribe(fn){
    if(!ch)return()=>{};
    const handler=e=>{const env=e?.data;if(env&&env.source&&env.type)fn(env)};
    ch.addEventListener('message',handler);
    return()=>ch.removeEventListener('message',handler);
  },
  close(){if(ch)ch.close()},
};
