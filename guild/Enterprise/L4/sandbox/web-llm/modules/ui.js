// ═══ UI helpers ═══
// DOM refs + tiny formatting utilities.

export const $=id=>document.getElementById(id);

export function esc(s){
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

export function formatSize(b){
  if(b<1024)return b+'B';
  if(b<1024*1024)return(b/1024).toFixed(1)+'K';
  return(b/1024/1024).toFixed(2)+'M';
}

// Fenced LLM output → chat HTML (tool actions → badges, code fences → <pre>)
export function formatLLMOutput(text){
  let s=esc(text);
  s=s.replace(/```\s*(create|edit|delete|preview|patch)\s+(\/[\w\-\.\/]+)\n([\s\S]*?)```/gi,
    (_,action,path)=>`<span class="tool-badge">${action} ${path}</span>`);
  s=s.replace(/```\s*commit\s+([\s\S]*?)```/gi,
    (_,msg)=>`<span class="tool-badge">commit: ${msg.trim()}</span>`);
  s=s.replace(/```\s*list\s*```/gi,'<span class="tool-badge">list files</span>');
  s=s.replace(/&lt;tool_call&gt;([\s\S]*?)&lt;\/tool_call&gt;/g,'<span class="tool-badge">tool</span>');
  s=s.replace(/&lt;path&gt;[\s\S]*?&lt;\/path&gt;/gi,'');
  s=s.replace(/&lt;content&gt;[\s\S]*?&lt;\/content&gt;/gi,'');
  s=s.replace(/```(\w*)\n([\s\S]*?)```/g,'<pre>$2</pre>');
  s=s.replace(/`([^`]+)`/g,'<code>$1</code>');
  s=s.replace(/\n/g,'<br>');
  return s;
}
