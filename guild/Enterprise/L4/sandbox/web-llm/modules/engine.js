// ═══ WebLLM engine wrapper ═══
// Loads the MLC WebLLM runtime on demand, publishes model/engine tags,
// exposes streaming completion + readiness accessors.

import {WEBLLM_URL} from './config.js';
import {MODEL,ENGINE} from './scada/providers.js';
import {mkUDT} from './scada/udt.js';

let webllm=null;
let engine=null;
let modelId=null;

export function isReady(){return !!engine}
export function getEngine(){return engine}
export function getModelId(){return modelId}

export async function checkGPU(){
  if(!navigator.gpu){
    MODEL.write('gpu',{available:false});
    return{ok:false,reason:'WebGPU not available'};
  }
  try{
    const adapter=await navigator.gpu.requestAdapter();
    const info=await adapter?.requestAdapterInfo?.()||{};
    MODEL.write('gpu',{available:true,vendor:info.vendor||null,architecture:info.architecture||null});
    return{ok:true,vendor:info.vendor,architecture:info.architecture};
  }catch(e){
    MODEL.write('gpu',{available:false,error:e.message});
    return{ok:false,reason:e.message};
  }
}

export async function loadModel(id,onProgress){
  modelId=id;
  MODEL.write('current',mkUDT('Model',{id,loaded:false,status:'importing'}));
  webllm=await import(WEBLLM_URL);
  MODEL.write('current',mkUDT('Model',{id,loaded:false,status:'loading'}));
  engine=await webllm.CreateMLCEngine(id,{
    initProgressCallback:(report)=>{
      const pct=Math.round((report.progress||0)*100);
      MODEL.write('current',mkUDT('Model',{id,loaded:false,progress:pct,status:report.text||'loading'}));
      onProgress?.(report);
    },
  });
  MODEL.write('current',mkUDT('Model',{id,loaded:true,progress:100,loadedAt:Date.now(),status:'ready'}));
  ENGINE.write('ready',true);
  return engine;
}

export async function* streamChat(messages,opts={}){
  if(!engine)throw new Error('engine not loaded');
  ENGINE.write('generating',true);
  const t0=performance.now();
  let tokens=0;
  try{
    const completion=await engine.chat.completions.create({
      messages,stream:true,
      max_tokens:opts.max_tokens??2048,
      temperature:opts.temperature??0.7,
    });
    for await(const chunk of completion){
      const delta=chunk.choices[0]?.delta?.content||'';
      if(delta){tokens++;yield delta}
    }
  }finally{
    const dt=performance.now()-t0;
    ENGINE.write('generating',false);
    ENGINE.write('streamedTokens',tokens,{type:'Counter'});
    ENGINE.write('lastLatencyMs',Math.round(dt),{type:'Gauge'});
  }
}
