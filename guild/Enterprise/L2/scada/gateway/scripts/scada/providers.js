// ═══ Tag providers ═══
// Namespaced helpers. Each provider owns a path prefix in the tag database
// and offers write/inc/del/read scoped to that prefix. Providers can also
// delete all their owned tags (useful on reset / room-change).

import * as tags from './tags.js';

export function provider(ns){
  const pfx=ns+'.';
  const p=k=>pfx+k;
  return {
    ns,
    write:(k,v,opts)=>tags.write(p(k),v,opts),
    inc:(k,by)=>tags.inc(p(k),by),
    del:(k)=>tags.del(p(k)),
    read:(k)=>tags.read(p(k)),
    clear(){
      for(const[path]of tags.list(pfx))tags.del(path);
    },
  };
}

// Registered providers (one per subsystem). Modules import these directly
// rather than calling provider() themselves.
export const SYS     = provider('sys');
export const AUTH    = provider('auth');
export const VERSION = provider('version');
export const ROOM    = provider('room');
export const TRACKER = provider('tracker');
export const PEERS   = provider('peers');
export const CHAT    = provider('chat');
export const SIGNAL  = provider('signal');
export const SANDBOX = provider('sandbox');

export const PROVIDERS={SYS,AUTH,VERSION,ROOM,TRACKER,PEERS,CHAT,SIGNAL,SANDBOX};
