// ═══ FS panel · file list + preview + commit log ═══

import {$,esc,formatSize} from './ui.js';
import {listFiles,readFile,getPreviewHTML,getPreviewableFiles,getLog,getRepoState,commitChanges} from './mcp-tools-engine.js';
import {FS,GIT} from './scada/providers.js';
import {mkUDT} from './scada/udt.js';

let selectedFile=null;
let currentPreview=null;

export function refreshFileList(){
  const{files,count}=listFiles('/');
  $('file-list').innerHTML='';
  $('file-count').textContent=count;
  for(const f of files){
    const div=document.createElement('div');
    div.className='file-entry'+(f.path===selectedFile?' active':'');
    const iconClass=f.type==='html'?'html':f.type==='css'?'css':f.type==='javascript'?'js':'other';
    const icon=f.type==='html'?'&#9671;':f.type==='css'?'&#9670;':f.type==='javascript'?'&#9674;':'&#9643;';
    div.innerHTML=`<span class="icon ${iconClass}">${icon}</span>
      <span class="name">${esc(f.path)}</span>
      <span class="size">${formatSize(f.size)}</span>`;
    div.onclick=()=>selectFile(f.path);
    $('file-list').appendChild(div);
  }
  FS.write('fileCount',count,{type:'Counter'});
  FS.write('files',files.map(f=>f.path));
  refreshPreviewTabs();
}

export function selectFile(path){
  selectedFile=path;
  refreshFileList();
  const f=readFile(path);
  if(f.ok&&f.type==='html')showPreview(path);
}

export function refreshPreviewTabs(){
  const{files}=getPreviewableFiles();
  const tabs=$('preview-tabs');tabs.innerHTML='';
  for(const f of files){
    const tab=document.createElement('div');
    tab.className='preview-tab'+(f===currentPreview?' active':'');
    tab.textContent=f.split('/').pop();
    tab.onclick=()=>showPreview(f);
    tabs.appendChild(tab);
  }
}

export function showPreview(path){
  const res=getPreviewHTML(path);
  if(!res.ok)return;
  currentPreview=path;
  $('no-preview').style.display='none';
  const host=$('iframe-container');
  host.style.display='block';host.innerHTML='';
  const iframe=document.createElement('iframe');
  iframe.sandbox='allow-scripts allow-same-origin';
  host.appendChild(iframe);
  iframe.srcdoc=res.html;
  FS.write('currentPreview',path);
  refreshPreviewTabs();refreshFileList();
}

export function clearPreview(){
  currentPreview=null;
  $('iframe-container').style.display='none';
  $('no-preview').style.display='flex';
  FS.del('currentPreview');
}

export function refreshCommitLog(){
  const{commits}=getLog(10);
  const box=$('commit-log');box.innerHTML='';
  for(const c of commits){
    const div=document.createElement('div');
    div.className='commit-entry';
    div.innerHTML=`<span class="cid">${esc(c.id)}</span> <span class="cmsg">${esc(c.message)}</span>`;
    box.appendChild(div);
  }
  const state=getRepoState();
  $('branch-display').textContent=state.branch;
  GIT.write('commitCount',state.commitCount,{type:'Counter'});
  GIT.write('branch',state.branch);
  if(commits[0])GIT.write('lastCommit',mkUDT('Commit',{id:commits[0].id,message:commits[0].message,ts:commits[0].timestamp}));
}

export function manualCommit(message){
  const r=commitChanges(message);
  refreshCommitLog();
  return r;
}

export function hasPreview(){return !!currentPreview}
export function getCurrentPreview(){return currentPreview}
