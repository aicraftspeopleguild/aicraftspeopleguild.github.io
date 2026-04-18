// ═══ MCP · shared repo state ═══
// Single source of truth for the in-memory virtual filesystem +
// git-lite + branch set. Every other mcp/ module mutates this object;
// none hold their own copies.
//
// See /controls/sandbox/web-llm/udts.json for the UDT shapes and
// /controls/sandbox/web-llm/tags.json for the published tag catalog.

import {bridge} from '../../../shared/mesh-bridge.js';

export const TOOL='web-llm';

// directories is a Set<string> of tracked dir paths (explicit mkdir).
// Files implicitly create their parent dirs on write.
export const repo={
  name:'my-project',
  branch:'main',
  files:new Map(),            // path -> {content, mtime}
  directories:new Set(['/']), // set of "/a/b" dir paths
  commits:[],                 // [{id, message, ts, branch, snapshot}]
  branches:new Map([['main',{head:null}]]), // name -> {head: commit id | null}
  staged:new Map(),           // reserved: pre-commit working-tree snapshot
};

// Flat envelope per §4: {source, type, path, value, ts}
export function publish(type,data){
  return bridge.publish(TOOL,type,{path:data?.path||null,value:data});
}

export const nextCommitId=()=>Math.random().toString(36).slice(2,9);
export const now=()=>Date.now();
export const normalize=p=>p.startsWith('/')?p:('/'+p);

// Strip trailing slash except for root.
export const normalizeDir=p=>{
  const n=normalize(p);
  return n.length>1&&n.endsWith('/')?n.slice(0,-1):n;
};

// Parent dir of a file path (always starts with '/', no trailing /).
export function parentDir(filePath){
  const p=normalize(filePath);
  const i=p.lastIndexOf('/');
  return i<=0?'/':p.slice(0,i);
}

// Ensure every ancestor of a file path is in directories.
export function ensureDirs(filePath){
  let d=parentDir(filePath);
  while(true){
    repo.directories.add(d);
    if(d==='/')break;
    d=parentDir(d);
  }
}

export function typeOf(path){
  const ext=(path.split('.').pop()||'').toLowerCase();
  return {html:'html',htm:'html',css:'css',js:'javascript',mjs:'javascript',
          json:'json',md:'markdown',txt:'text',svg:'svg',
          png:'image',jpg:'image',jpeg:'image',gif:'image',webp:'image'}[ext]||'other';
}

// Current branch head commit snapshot (or empty object).
export function headSnapshot(){
  const b=repo.branches.get(repo.branch);
  if(!b||!b.head)return {};
  const c=repo.commits.find(x=>x.id===b.head);
  return c?.snapshot||{};
}
