// ═══ Web-LLM sandbox · entry point ═══

import {$,esc} from './ui.js';
import {MODELS,DEFAULT_REPO,EMOTION_KEYS} from './config.js';
import {checkGPU,loadModel,streamChat,isReady,getModelId} from './engine.js';
import {setupMic,setupRecognition,toggleListening,startListeningAuto,configure as configureVoice,
        emotionSnapshot,voice} from './voice.js';
import {addMsg,addSystemMsg,updateMsgText,pushHistory,recentHistory} from './chat.js';
import {parseAndRunAll,logRow,runToolCall} from './tools.js';
import {refreshFileList,refreshCommitLog,showPreview,manualCommit,clearPreview,getCurrentPreview,hasPreview} from './fs-panel.js';
import {initRepo,getRepoState,buildToolSystemPrompt} from './mcp-tools-engine.js';
import {SYS,FS} from './scada/providers.js';

let isGenerating=false;

// ─── Populate model <select> from config ───
(function hydrateSelect(){
  const sel=$('model-select');sel.innerHTML='';
  for(const m of MODELS){
    const opt=document.createElement('option');
    opt.value=m.id;opt.textContent=m.label;
    if(m.selected)opt.selected=true;
    sel.appendChild(opt);
  }
})();

// ─── GPU probe ───
checkGPU().then(res=>{
  const el=$('gpu-status');
  if(res.ok){
    el.textContent=`WebGPU OK — ${res.vendor||'GPU'} ${res.architecture||''}`.trim();
    el.className='ok';
  }else{
    el.textContent='WebGPU '+(res.reason==='WebGPU not available'?'not available — model inference disabled':'detection failed');
    el.className='fail';
    $('load-btn').textContent='WebGPU Required for LLM';
    $('load-btn').disabled=true;
  }
});

// ─── Load flow ───
$('load-btn').onclick=async()=>{
  const id=$('model-select').value;
  $('load-btn').disabled=true;
  $('load-progress').style.display='block';
  $('load-status').textContent='Importing WebLLM...';
  try{
    await loadModel(id,(report)=>{
      const pct=Math.round((report.progress||0)*100);
      $('load-bar').style.width=pct+'%';
      $('load-status').textContent=report.text||`Loading... ${pct}%`;
    });
    $('model-status').textContent=id.split('-').slice(0,3).join('-');
    $('model-status').style.color='var(--green)';
    $('load-overlay').style.display='none';
    startSandbox();
  }catch(e){
    $('load-status').textContent='Error: '+e.message;
    $('load-btn').disabled=false;
  }
};

$('skip-btn').onclick=()=>{
  $('load-overlay').style.display='none';
  $('model-status').textContent='No model (sandbox only)';
  startSandbox();
};

// ─── Sandbox bootstrap ───
async function startSandbox(){
  SYS.write('startedAt',Date.now(),{type:'DateTime'});
  SYS.write('userAgent',navigator.userAgent);

  initRepo(DEFAULT_REPO);
  $('repo-name-display').textContent=DEFAULT_REPO;
  refreshFileList();refreshCommitLog();

  const loaded=isReady();
  addSystemMsg('Sandbox initialized. '+(loaded
    ?'AI model loaded — talk or type to start building!'
    :'No AI model — you can still create files manually.'));

  // Voice pipeline
  configureVoice({
    onLevel:(pct)=>{
      $('mic-level-fill').style.width=pct+'%';
      $('mic-level-fill').style.background=pct>70?'var(--orange)':pct>40?'var(--green)':'var(--accent)';
      $('mic-level-label').textContent=pct+'%';
      $('mic-indicator').classList.toggle('active',pct>5);
    },
    onStatus:(t)=>{$('voice-status').textContent=t},
    onTranscriptInterim:(t)=>{
      $('voice-status').textContent='🎤 '+t;
      $('chat-input').value=t;
      $('chat-input').style.borderColor='var(--green)';
    },
    onTranscriptFinal:(t)=>{
      $('voice-status').textContent='Listening — speak to chat...';
      $('chat-input').value='';
      $('chat-input').style.borderColor='';
      sendMessage(t);
    },
  });

  await setupMic();
  setupRecognition();
  if(await startListeningAuto()){
    $('btn-mic').classList.add('active');
  }

  // Emotion dots refresh loop (throttled)
  setInterval(updateEmotionDots,200);
}

function updateEmotionDots(){
  const snap=emotionSnapshot();
  const dots=document.querySelectorAll('.emo-dot');
  EMOTION_KEYS.forEach((k,i)=>{
    const v=snap.values[k]||0;
    const dot=dots[i];if(!dot)return;
    dot.classList.toggle('active',v>0.4);
    dot.style.opacity=0.2+v*0.8;
  });
}

// ─── Send ───
async function sendMessage(text){
  if(!text.trim()||isGenerating)return;
  isGenerating=true;

  const snap=emotionSnapshot();
  const emoTag=snap.dominant+' '+Math.round((snap.values[snap.dominant]||0)*100)+'%';
  addMsg('user',text,emoTag);
  $('chat-input').value='';

  if(!isReady()){
    addSystemMsg('Voice captured: "'+text+'" — Load a model to get AI responses.');
    isGenerating=false;return;
  }

  const state=getRepoState();
  const repoCtx=state.fileCount>0
    ?`\nCURRENT REPO: ${state.fileCount} files (${state.files.join(', ')}), ${state.commitCount} commits on branch '${state.branch}'.`
    :'';
  const systemPrompt=buildToolSystemPrompt()
    +`\n\nUSER EMOTION STATE: The user currently sounds ${snap.dominant} (${Math.round((snap.values[snap.dominant]||0)*100)}% intensity). Emotions: ${Object.entries(snap.values).map(([k,v])=>k+':'+Math.round(v*100)+'%').join(', ')}. Adapt your tone accordingly.`
    +repoCtx;

  const messages=[{role:'system',content:systemPrompt},...recentHistory(16),{role:'user',content:text}];

  const aiDiv=addMsg('ai','...');
  try{
    let full='';
    for await(const delta of streamChat(messages,{max_tokens:2048,temperature:0.7})){
      full+=delta;
      updateMsgText(aiDiv,full+' ▍');
    }
    updateMsgText(aiDiv,full);
    pushHistory('user',text);
    pushHistory('assistant',full);

    // Tool execution pass
    const{calls}=parseAndRunAll(full,(tc,result)=>{
      if(tc.name==='preview'&&result.ok)showPreview(tc.args.path);
      else if((tc.name==='create_file'||tc.name==='edit_file')&&result.ok){
        const p=tc.args.path||'';
        if(p.endsWith('.html')||p.endsWith('.htm'))showPreview(p);
      }
    });

    if(calls.length>0){
      refreshFileList();refreshCommitLog();

      // Follow-up turn with tool results
      const toolSummary=calls.map(tc=>`Tool ${tc.name}: ok`).join('\n');
      pushHistory('user',`[Tool Results]\n${toolSummary}\n[Continue based on these results. HTML files you created are now in the preview.]`);

      const followMsgs=[{role:'system',content:systemPrompt},...recentHistory(20)];
      let follow='';
      const followDiv=addMsg('ai','...');
      for await(const delta of streamChat(followMsgs,{max_tokens:1024,temperature:0.7})){
        follow+=delta;updateMsgText(followDiv,follow+' ▍');
      }
      updateMsgText(followDiv,follow);
      pushHistory('assistant',follow);

      const{calls:more}=parseAndRunAll(follow,(tc,result)=>{
        if((tc.name==='create_file'||tc.name==='edit_file'||tc.name==='preview')&&result.ok){
          const p=tc.args?.path||'';
          if(p.endsWith('.html')||p.endsWith('.htm')||tc.name==='preview')showPreview(p);
        }
      });
      if(more.length>0){refreshFileList();refreshCommitLog()}
    }
  }catch(e){
    updateMsgText(aiDiv,'Error: '+e.message);
  }
  isGenerating=false;
}

// ─── Wire handlers ───
$('chat-input').addEventListener('keydown',(e)=>{
  if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage($('chat-input').value)}
});
$('btn-send').onclick=()=>sendMessage($('chat-input').value);

$('btn-mic').onclick=async()=>{
  const on=await toggleListening();
  $('btn-mic').classList.toggle('active',on);
};

$('btn-new-repo').onclick=()=>{
  const name=prompt('Repo name:','my-project');
  if(!name)return;
  initRepo(name);
  $('repo-name-display').textContent=name;
  clearPreview();refreshFileList();refreshCommitLog();
  addSystemMsg(`New repo "${name}" initialized.`);
};

$('btn-commit').onclick=()=>{
  const msg=prompt('Commit message:','Update files');
  if(!msg)return;
  const r=manualCommit(msg);
  logRow('commit',{message:msg},r);
  addSystemMsg(`Committed: ${msg} (${r.id})`);
};

$('btn-refresh-preview').onclick=()=>{
  if(hasPreview())showPreview(getCurrentPreview());
};
