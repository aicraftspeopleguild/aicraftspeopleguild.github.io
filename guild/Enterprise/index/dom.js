// ── DOM utilities ─────────────────────────────────────────────────────

export const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
export const fmtTs=ts=>ts?new Date(ts).toLocaleTimeString():'—';

export function el(tag,attrs={},children=[]){
  const node=document.createElement(tag);
  for(const[k,v]of Object.entries(attrs)){
    if(k==='class')node.className=v;
    else if(k==='html')node.innerHTML=v;
    else node.setAttribute(k,v);
  }
  for(const c of[].concat(children||[]))if(c!=null)node.append(c.nodeType?c:document.createTextNode(c));
  return node;
}
