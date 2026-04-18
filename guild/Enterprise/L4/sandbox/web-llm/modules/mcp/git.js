// ═══ MCP · git-lite ═══
// Single-branch by default, multi-branch after a branch <name> call.
// All operations share /controls/sandbox/web-llm/modules/mcp/repo.js.

import {repo,publish,now,nextCommitId,headSnapshot} from './repo.js';

export function initRepo(name='my-project'){
  repo.name=name;
  repo.branch='main';
  repo.files.clear();
  repo.directories.clear();repo.directories.add('/');
  repo.commits.length=0;
  repo.staged.clear();
  repo.branches.clear();repo.branches.set('main',{head:null});
  publish('init_repo',{name});
  return{ok:true,name,branch:'main'};
}

export function commitChanges(message='update'){
  const id=nextCommitId();
  const snapshot={};
  for(const[p,f]of repo.files)snapshot[p]=f.content;
  const commit={id,message,ts:now(),branch:repo.branch,snapshot};
  repo.commits.unshift(commit);
  const b=repo.branches.get(repo.branch)||{head:null};
  b.head=id;
  repo.branches.set(repo.branch,b);
  publish('commit',{id,message,files:Object.keys(snapshot).length,branch:repo.branch});
  return{ok:true,id,message,files:Object.keys(snapshot).length,branch:repo.branch};
}

export function getLog(n=20){
  return{
    commits:repo.commits.slice(0,n).map(c=>({
      id:c.id,message:c.message,ts:c.ts,branch:c.branch||'main',
    })),
  };
}

// Diff working-tree vs a ref (default = current branch HEAD).
export function getDiff(ref){
  let base;
  if(ref){
    const c=repo.commits.find(x=>x.id===ref);
    if(!c)return{ok:false,error:'unknown ref: '+ref};
    base=c.snapshot;
  }else{
    base=headSnapshot();
  }
  const added=[],modified=[],deleted=[];
  for(const[p,f]of repo.files){
    if(!(p in base))added.push(p);
    else if(base[p]!==f.content)modified.push(p);
  }
  for(const p of Object.keys(base))if(!repo.files.has(p))deleted.push(p);
  const result={ok:true,ref:ref||repo.branches.get(repo.branch)?.head||null,added,modified,deleted};
  publish('diff',{ref:result.ref,added:added.length,modified:modified.length,deleted:deleted.length});
  return result;
}

// Summary of the working tree vs HEAD. clean=true when nothing pending.
export function getStatus(){
  const d=getDiff();
  const clean=!d.added.length&&!d.modified.length&&!d.deleted.length;
  const result={ok:true,clean,
    added:d.added,modified:d.modified,deleted:d.deleted,
    commits:repo.commits.length,branch:repo.branch};
  publish('status',{clean,branch:repo.branch,
    added:d.added.length,modified:d.modified.length,deleted:d.deleted.length});
  return result;
}

export function checkout(ref){
  const c=repo.commits.find(x=>x.id===ref);
  if(!c)return{ok:false,error:'unknown ref: '+ref};
  repo.files.clear();
  for(const[p,content]of Object.entries(c.snapshot))repo.files.set(p,{content,mtime:now()});
  publish('checkout',{id:ref});
  return{ok:true,id:ref,files:Object.keys(c.snapshot).length};
}

export function branch(name){
  const n=String(name||'').trim();
  if(!n)return{ok:false,error:'branch name required'};
  // switch to existing
  if(repo.branches.has(n)){
    repo.branch=n;
    publish('branch',{name:n,action:'switch'});
    return{ok:true,name:n,action:'switch',head:repo.branches.get(n).head};
  }
  // create new off current HEAD
  const curHead=repo.branches.get(repo.branch)?.head||null;
  repo.branches.set(n,{head:curHead});
  repo.branch=n;
  publish('branch',{name:n,action:'create'});
  return{ok:true,name:n,action:'create',head:curHead};
}

export function listBranches(){
  return{
    current:repo.branch,
    branches:[...repo.branches.entries()].map(([name,b])=>({
      name,head:b.head,commitCount:repo.commits.filter(c=>c.branch===name).length,
    })),
  };
}

export function getRepoState(){
  return{
    name:repo.name,
    branch:repo.branch,
    fileCount:repo.files.size,
    dirCount:repo.directories.size,
    files:[...repo.files.keys()],
    directories:[...repo.directories],
    commitCount:repo.commits.length,
    branches:[...repo.branches.keys()],
  };
}

// Export the full state as a single JSON string. Round-trips via importRepo.
export function exportRepo(){
  const snapshot={
    name:repo.name,branch:repo.branch,
    files:Object.fromEntries([...repo.files].map(([p,f])=>[p,f.content])),
    directories:[...repo.directories],
    commits:repo.commits,
    branches:Object.fromEntries(repo.branches),
  };
  const json=JSON.stringify(snapshot,null,2);
  publish('export',{format:'json',size:json.length});
  return{ok:true,format:'json',size:json.length,json};
}

export function importRepo(json){
  let data;
  try{data=typeof json==='string'?JSON.parse(json):json}
  catch(e){return{ok:false,error:'invalid JSON: '+e.message}}
  if(!data||typeof data!=='object')return{ok:false,error:'empty payload'};
  repo.name=data.name||repo.name;
  repo.branch=data.branch||'main';
  repo.files.clear();
  for(const[p,content]of Object.entries(data.files||{})){
    repo.files.set(p,{content,mtime:now()});
  }
  repo.directories.clear();repo.directories.add('/');
  for(const d of data.directories||[])repo.directories.add(d);
  repo.commits.length=0;
  for(const c of data.commits||[])repo.commits.push(c);
  repo.branches.clear();
  for(const[n,b]of Object.entries(data.branches||{main:{head:null}}))
    repo.branches.set(n,b);
  if(!repo.branches.has(repo.branch))repo.branches.set(repo.branch,{head:null});
  publish('import',{files:repo.files.size,commits:repo.commits.length,branch:repo.branch});
  return{ok:true,name:repo.name,branch:repo.branch,
    files:repo.files.size,commits:repo.commits.length};
}
