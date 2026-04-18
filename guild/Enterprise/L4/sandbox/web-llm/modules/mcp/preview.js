// ═══ MCP · preview + bundle ═══
// Resolve sibling-file references inline so an HTML file in the VFS can
// render in an <iframe srcdoc> without a real server. Bundle emits the
// self-contained preview HTML as a string (or Blob URL) for export.

import {repo,publish,normalize,typeOf} from './repo.js';

export function getPreviewableFiles(){
  const files=[];
  for(const p of repo.files.keys())if(typeOf(p)==='html')files.push(p);
  files.sort();
  return{files};
}

// Inline same-repo <link rel=stylesheet href>, <script src>, and <img src>
// references so the iframe renders the HTML without network access.
export function getPreviewHTML(path){
  const p=normalize(path);
  const f=repo.files.get(p);
  if(!f)return{ok:false,error:'not found: '+p};
  if(typeOf(p)!=='html')return{ok:false,error:'not html: '+p};
  const dir=p.replace(/\/[^\/]*$/,'')||'/';
  const inlined=[];

  const resolve=rel=>{
    if(!rel)return null;
    if(/^(?:[a-z]+:)?\/\//i.test(rel))return null;  // absolute URL
    if(rel.startsWith('data:'))return null;
    if(rel.startsWith('/'))return rel;
    return (dir==='/'?'':dir)+'/'+rel.replace(/^\.\//,'');
  };

  let html=f.content;

  html=html.replace(
    /<link\s+[^>]*rel=["']?stylesheet["']?[^>]*href=["']([^"']+)["'][^>]*>/gi,
    (m,href)=>{
      const abs=resolve(href);
      const css=abs&&repo.files.get(abs)?.content;
      if(!css)return m;
      inlined.push({path:abs,kind:'css'});
      return `<style>/* ${abs} */\n${css}\n</style>`;
    }
  );

  html=html.replace(
    /<script\s+[^>]*src=["']([^"']+)["'][^>]*>\s*<\/script>/gi,
    (m,src)=>{
      const abs=resolve(src);
      const js=abs&&repo.files.get(abs)?.content;
      if(!js)return m;
      inlined.push({path:abs,kind:'js'});
      return `<script>/* ${abs} */\n${js}\n<\/script>`;
    }
  );

  // inline SVG images via data URI (image/svg+xml)
  html=html.replace(
    /<img\s+[^>]*src=["']([^"']+)["'][^>]*>/gi,
    (m,src)=>{
      const abs=resolve(src);
      if(!abs||!abs.toLowerCase().endsWith('.svg'))return m;
      const svg=repo.files.get(abs)?.content;
      if(!svg)return m;
      inlined.push({path:abs,kind:'img'});
      const b64=btoa(unescape(encodeURIComponent(svg)));
      return m.replace(src,'data:image/svg+xml;base64,'+b64);
    }
  );

  publish('preview',{path:p,sizeBytes:html.length,inlined:inlined.length});
  return{ok:true,html,path:p,sizeBytes:html.length,inlined};
}

// Return a Blob URL for the self-contained preview HTML so it can be
// opened in a new tab or downloaded.
export function getPreviewBlobUrl(path){
  const r=getPreviewHTML(path);
  if(!r.ok)return r;
  const blob=new Blob([r.html],{type:'text/html'});
  const url=URL.createObjectURL(blob);
  return{ok:true,path:r.path,url,sizeBytes:r.html.length};
}

// Bundle: identical to getPreviewHTML but tagged with 'bundle' event so
// SCADA distinguishes "operator previewed" from "operator exported".
export function bundle(path){
  const r=getPreviewHTML(path);
  if(!r.ok)return r;
  publish('bundle',{path:r.path,sizeBytes:r.sizeBytes});
  return{ok:true,format:'bundle',path:r.path,html:r.html,sizeBytes:r.sizeBytes};
}
