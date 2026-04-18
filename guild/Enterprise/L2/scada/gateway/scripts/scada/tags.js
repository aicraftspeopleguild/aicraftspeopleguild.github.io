// ═══ SCADA tag database ═══
// Path-addressed runtime registry. Each tag carries {value, quality, ts, type}.
// Writes publish to subscribers (exact path or '.*' / '.**' wildcards).

const tags=new Map();
const subs=new Map(); // pattern -> Set<fn>

const now=()=>Date.now();

function patternMatches(pat,path){
  if(pat===path||pat==='*'||pat==='**')return true;
  if(pat.endsWith('.**'))return path.startsWith(pat.slice(0,-2));
  if(pat.endsWith('.*')){
    const base=pat.slice(0,-1);
    if(!path.startsWith(base))return false;
    return !path.slice(base.length).includes('.');
  }
  return false;
}

function notify(path){
  const tag=tags.get(path);
  for(const[pat,fns]of subs){
    if(patternMatches(pat,path))for(const fn of fns){try{fn(path,tag)}catch(e){}}
  }
}

export function write(path,value,opts={}){
  const tag={
    value,
    quality:opts.quality||'good',
    ts:now(),
    type:opts.type||(value&&typeof value==='object'&&value._udt)||null,
  };
  tags.set(path,tag);
  notify(path);
  return tag;
}

export function inc(path,by=1){
  const cur=tags.get(path);
  return write(path,(cur?.value||0)+by,{type:'Counter'});
}

export function read(path){return tags.get(path)||null}

export function del(path){
  if(tags.delete(path))notify(path);
}

export function list(prefix=''){
  const out=[];
  for(const[p,t]of tags)if(!prefix||p.startsWith(prefix))out.push([p,t]);
  out.sort((a,b)=>a[0].localeCompare(b[0]));
  return out;
}

export function subscribe(pattern,fn){
  if(!subs.has(pattern))subs.set(pattern,new Set());
  subs.get(pattern).add(fn);
  return()=>{const s=subs.get(pattern);if(s){s.delete(fn);if(!s.size)subs.delete(pattern)}};
}

export function setQuality(path,quality){
  const t=tags.get(path);if(!t)return;
  if(t.quality!==quality){t.quality=quality;notify(path)}
}

// Sweep: mark any tag older than ageMs as 'stale'.
export function sweepStale(prefix,ageMs){
  const cut=now()-ageMs;
  for(const[p,t]of tags){
    if(prefix&&!p.startsWith(prefix))continue;
    if(t.quality==='good'&&t.ts<cut){t.quality='stale';notify(p)}
  }
}
