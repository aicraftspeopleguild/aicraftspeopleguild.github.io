// ═══ MCP · virtual filesystem ═══
// Every mutation publishes a bridge envelope so sandbox.web-llm.* tags
// pick the change up in the main ACG SCADA monitor.

import {repo,publish,now,normalize,normalizeDir,parentDir,ensureDirs,typeOf} from './repo.js';

export function createFile(path,content=''){
  const p=normalize(path);
  if(repo.files.has(p))return{ok:false,error:'file exists: '+p};
  ensureDirs(p);
  repo.files.set(p,{content,mtime:now()});
  publish('create_file',{path:p,size:content.length});
  return{ok:true,path:p,size:content.length};
}

export function editFile(path,content=''){
  const p=normalize(path);
  if(!repo.files.has(p))return createFile(p,content);
  repo.files.get(p).content=content;
  repo.files.get(p).mtime=now();
  publish('edit_file',{path:p,size:content.length});
  return{ok:true,path:p,size:content.length};
}

export function patchFile(path,oldStr,newStr){
  const p=normalize(path);
  const f=repo.files.get(p);
  if(!f)return{ok:false,error:'not found: '+p};
  if(!f.content.includes(oldStr))return{ok:false,error:'oldStr not found'};
  f.content=f.content.replace(oldStr,newStr);
  f.mtime=now();
  publish('patch_file',{path:p,size:f.content.length});
  return{ok:true,path:p,size:f.content.length};
}

export function readFile(path){
  const p=normalize(path);
  const f=repo.files.get(p);
  if(!f)return{ok:false,error:'not found: '+p};
  return{ok:true,path:p,content:f.content,type:typeOf(p),size:f.content.length};
}

export function deleteFile(path){
  const p=normalize(path);
  if(!repo.files.has(p))return{ok:false,error:'not found: '+p};
  repo.files.delete(p);
  publish('delete_file',{path:p});
  return{ok:true,path:p};
}

export function listFiles(prefix='/'){
  const files=[];
  for(const[p,f]of repo.files){
    if(!prefix||prefix==='/'||p.startsWith(prefix)){
      files.push({path:p,type:typeOf(p),size:f.content.length,mtime:f.mtime});
    }
  }
  files.sort((a,b)=>a.path.localeCompare(b.path));
  return{count:files.length,files};
}

export function searchFiles(query){
  const q=String(query||'').toLowerCase();
  const results=[];
  if(!q)return{results,count:0};
  for(const[p,f]of repo.files){
    const hay=f.content.toLowerCase();
    let i=0,hits=0;
    while((i=hay.indexOf(q,i))!==-1){hits++;i+=q.length}
    if(hits)results.push({path:p,matches:hits});
  }
  return{results,count:results.length};
}

export function getAllFiles(){
  const out={};
  for(const[p,f]of repo.files)out[p]=f.content;
  return out;
}

/* ═══ NEW repo-building primitives ═══ */

export function mkdir(path){
  const p=normalizeDir(path);
  if(repo.directories.has(p))return{ok:false,error:'dir exists: '+p};
  repo.directories.add(p);
  // also record parents
  let d=parentDir(p);
  while(true){repo.directories.add(d);if(d==='/')break;d=parentDir(d)}
  publish('mkdir',{path:p});
  return{ok:true,path:p};
}

export function moveFile(from,to){
  const a=normalize(from),b=normalize(to);
  const f=repo.files.get(a);
  if(!f)return{ok:false,error:'not found: '+a};
  if(repo.files.has(b))return{ok:false,error:'dest exists: '+b};
  repo.files.delete(a);
  ensureDirs(b);
  repo.files.set(b,{content:f.content,mtime:now()});
  publish('mv',{path:b,from:a});
  return{ok:true,from:a,to:b};
}

export function copyFile(from,to){
  const a=normalize(from),b=normalize(to);
  const f=repo.files.get(a);
  if(!f)return{ok:false,error:'not found: '+a};
  if(repo.files.has(b))return{ok:false,error:'dest exists: '+b};
  ensureDirs(b);
  repo.files.set(b,{content:f.content,mtime:now()});
  publish('cp',{path:b,from:a});
  return{ok:true,from:a,to:b,size:f.content.length};
}

// Hierarchical listing. Nodes include both dirs and files under `prefix`.
export function tree(prefix='/'){
  const root=normalizeDir(prefix);
  const nodes=[];
  for(const d of repo.directories){
    if(d===root||d.startsWith(root==='/'?'/':root+'/'))
      nodes.push({path:d,type:'dir',size:null});
  }
  for(const[p,f]of repo.files){
    if(root==='/'||p===root||p.startsWith(root+'/'))
      nodes.push({path:p,type:typeOf(p),size:f.content.length});
  }
  nodes.sort((a,b)=>a.path.localeCompare(b.path));
  const fileCount=nodes.filter(n=>n.type!=='dir').length;
  publish('tree',{path:root,fileCount});
  return{root,nodes,fileCount};
}
