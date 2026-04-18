export const $=id=>document.getElementById(id);
export const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

export function log(t,c=''){
  const d=document.createElement('div');d.className='lg '+c;d.textContent=t;
  $('log').appendChild(d);$('log').scrollTop=$('log').scrollHeight;
  while($('log').children.length>50)$('log').removeChild($('log').firstChild);
}

// 🟢🟡🔴 status badges
export function badge(state){
  const dot=$('dot'),tx=$('cTx'),bg=$('cBg');
  if(state==='connecting'){dot.className='dt try';tx.textContent='Connecting';bg.textContent='Connecting';bg.className='bg a';}
  else if(state==='connected'){dot.className='dt on';tx.textContent='Connected';bg.textContent='Connected';bg.className='bg s';}
  else if(state==='reconnecting'){dot.className='dt try';tx.textContent='Reconnecting';bg.textContent='Reconnecting';bg.className='bg a';}
  else if(state==='offline'){dot.className='dt off';tx.textContent='No tracker';bg.textContent='Offline';bg.className='bg r';}
}
