// ═══ Tool dispatch + HMI row logging ═══

import {$,esc} from './ui.js';
import {executeTool,parseToolCalls} from './mcp-tools-engine.js';
import {TOOL} from './scada/providers.js';
import {mkUDT} from './scada/udt.js';

let callCount=0;

export function runToolCall(name,args){
  const result=executeTool(name,args||{});
  logRow(name,args||{},result);
  return result;
}

export function parseAndRunAll(text,onAfter){
  const calls=parseToolCalls(text);
  const results=[];
  for(const tc of calls){
    const r=runToolCall(tc.name,tc.args);
    results.push({call:tc,result:r});
    onAfter?.(tc,r);
  }
  return{calls,results};
}

export function logRow(name,args,result){
  callCount++;
  $('tool-count').textContent=callCount;
  TOOL.inc('count');
  TOOL.write('last',mkUDT('ToolCall',{
    name,
    args:truncateArgs(args),
    ok:!!result.ok,
    result:result.ok?(result.path||result.id||'ok'):result.error,
    ts:Date.now(),
  }));

  const argsStr=Object.entries(args||{}).map(([k,v])=>{
    const s=typeof v==='string'?(v.length>60?v.slice(0,60)+'...':v):JSON.stringify(v);
    return `${k}=${s}`;
  }).join(', ');
  const resClass=result.ok?'ok':'err';
  const resText=result.ok
    ?(result.path||result.id||result.summary||(result.count!==undefined?`${result.count} items`:'OK'))
    :result.error;

  const div=document.createElement('div');
  div.className='tool-entry';
  div.innerHTML=`<span class="tool-time">${new Date().toLocaleTimeString()}</span>
    <span class="tool-name">${esc(name)}</span>
    <div class="tool-args">${esc(argsStr)}</div>
    <div class="tool-result ${resClass}">${result.ok?'✓':'✗'} ${esc(String(resText))}</div>`;
  $('tool-log').prepend(div);
}

function truncateArgs(args){
  const out={};
  for(const[k,v]of Object.entries(args||{})){
    if(typeof v==='string'&&v.length>120)out[k]=v.slice(0,120)+'…';
    else out[k]=v;
  }
  return out;
}
