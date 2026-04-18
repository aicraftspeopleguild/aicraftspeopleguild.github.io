import {$,log} from './ui.js';
import {TRACKERS,myId,myNm,myEm} from './config.js';
import {pm,updPeers} from './peers.js';
import {send} from './chat.js';
import {join,announce,wsReady} from './p2p.js';
import {startVersion} from './version.js';
import {startAuth,onProfileChange,getProfile} from './auth.js';
import {startMonitor,toggle as toggleMonitor} from './scada/monitor.js';
import {SYS} from './scada/providers.js';
import {startSandboxBridge} from './sandbox-bridge.js';
import {startErrorCapture} from './errors.js';

function meLabel(){const p=getProfile();return p?.username||myNm}

$('mId').textContent=meLabel();

$('jBtn').onclick=()=>join($('rIn').value.trim()||'acg-guild');
$('cIn').onkeydown=e=>{if(e.key==='Enter')send()};
$('sBtn').onclick=send;
// #scBtn replaced with a link to /controls/; Ctrl+. still toggles the SCADA drawer below.

// keyboard: ctrl/cmd+. → toggle SCADA
window.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='.'){e.preventDefault();toggleMonitor()}});

log('⚒ ACG P2P Mesh v1.1','hi');
log('peer: '+myId+' (20 bytes ✓)','hi');
log('trackers: '+TRACKERS.length+' with auto-fallback','hi');

// sys.* tags
SYS.write('startedAt',Date.now(),{type:'DateTime'});
SYS.write('myId',myId);SYS.write('myNm',myNm);SYS.write('myEm',myEm);
SYS.write('trackerCount',TRACKERS.length,{type:'Counter'});
SYS.write('userAgent',navigator.userAgent);

startErrorCapture();
startMonitor();
startSandboxBridge();
updPeers();
startVersion();
startAuth();

onProfileChange(p=>{
  $('mId').textContent=meLabel();
  updPeers();
  // re-send hi to open peers so they pick up new name/avatar
  const me=getProfile();
  const hi=JSON.stringify({t:'hi',id:myId,nm:me?.username||myNm,em:myEm,av:me?.avatar||null});
  for(const[,info]of pm)for(const dc of info.dcs)if(dc.readyState==='open'){try{dc.send(hi)}catch(e){}}
});

setTimeout(()=>join($('rIn').value.trim()||'acg-guild'),300);

// periodic re-announce + uptime tick
setInterval(()=>{if(wsReady())announce()},30000);
setInterval(()=>SYS.write('uptimeSec',Math.floor((Date.now()-SYS.read('startedAt').value)/1000),{type:'Counter'}),1000);
