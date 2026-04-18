// ═══ Web-LLM tag providers ═══
// Namespaced wrappers around the local tag plant.

import * as tags from './tags.js';

export function provider(ns){
  const pfx=ns+'.';
  const p=k=>pfx+k;
  return{
    ns,
    write:(k,v,opts)=>tags.write(p(k),v,opts),
    inc:(k,by)=>tags.inc(p(k),by),
    del:(k)=>tags.del(p(k)),
    read:(k)=>tags.read(p(k)),
    clear(){for(const[path]of tags.list(pfx))tags.del(path)},
  };
}

export const SYS     = provider('sys');
export const MODEL   = provider('model');
export const ENGINE  = provider('engine');
export const VOICE   = provider('voice');
export const EMOTION = provider('emotion');
export const FS      = provider('fs');
export const GIT     = provider('git');
export const CHAT    = provider('chat');
export const TOOL    = provider('tool');

export const PROVIDERS={SYS,MODEL,ENGINE,VOICE,EMOTION,FS,GIT,CHAT,TOOL};
