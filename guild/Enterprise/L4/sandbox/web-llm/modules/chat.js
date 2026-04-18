// ═══ Chat rendering + history ═══

import {$,formatLLMOutput} from './ui.js';
import {CHAT} from './scada/providers.js';
import {mkUDT} from './scada/udt.js';

export const chatHistory=[];

export function addMsg(role,text,emoTag=''){
  const div=document.createElement('div');
  div.className='msg '+role;
  const sender=role==='user'?'You':role==='ai'?'AI':'System';
  const emo=emoTag?`<span class="emo-tag" style="background:rgba(255,255,255,.08)">${emoTag}</span>`:'';
  div.innerHTML=`<div class="sender">${sender}${emo}</div>${formatLLMOutput(text)}`;
  const box=$('chat-messages');
  box.appendChild(div);box.scrollTop=box.scrollHeight;
  CHAT.inc('msgs');
  CHAT.write('last',mkUDT('ChatMsg',{role,len:text.length,ts:Date.now(),emoTag:emoTag||null}));
  return div;
}

export function addSystemMsg(text){return addMsg('system',text)}

export function updateMsgText(div,text){
  const senderHtml=div.querySelector('.sender').outerHTML;
  div.innerHTML=senderHtml+formatLLMOutput(text);
  const box=$('chat-messages');box.scrollTop=box.scrollHeight;
}

export function pushHistory(role,content){
  chatHistory.push({role,content});
  if(chatHistory.length>32)chatHistory.splice(0,chatHistory.length-32);
}

export function recentHistory(n=16){
  return chatHistory.slice(-n).filter(m=>m.role==='user'||m.role==='assistant');
}
