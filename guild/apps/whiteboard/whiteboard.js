// ═══ ACG P2P Whiteboard ═══
// Boots the mesh (join/bcast/peers), renders a shared canvas, broadcasts
// strokes over WebRTC data channels via t:'wb' messages. Plugin hook
// registerPeerHandler routes inbound strokes from peers into the canvas.
import {myId,myNm,myEm} from '../../Enterprise/L2/scada/gateway/scripts/config.js';
import {join,bcast,wsReady,announce} from '../../Enterprise/L2/scada/gateway/scripts/p2p.js';
import {pm,registerPeerHandler,updPeers} from '../../Enterprise/L2/scada/gateway/scripts/peers.js';
import {log} from '../../Enterprise/L2/scada/gateway/scripts/ui.js';
import {startAuth} from '../../Enterprise/L2/scada/gateway/scripts/auth.js';
import {startErrorCapture} from '../../Enterprise/L2/scada/gateway/scripts/errors.js';

// ── identity
const $=id=>document.getElementById(id);
$('mId').textContent=myId.slice(-8);

// ── room from URL hash (#room=foo) or default
const params=new URLSearchParams(location.hash.slice(1));
const roomName=params.get('room')||$('rIn').value.trim()||'acg-whiteboard';
$('rIn').value=roomName;

// ── canvas state (mirrors sandbox whiteboard)
const cv=$('wb'),ctx=cv.getContext('2d');
let tool='pen',color=$('wb-color').value,size=parseInt($('wb-size').value,10);
let strokes=[]; // {id,color,size,erase,pts:[{x,y}]}

function fitCanvas(){
  const dpr=window.devicePixelRatio||1;
  const r=cv.parentElement.getBoundingClientRect();
  cv.width=Math.floor(r.width*dpr);
  cv.height=Math.floor(r.height*dpr);
  ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.lineCap=ctx.lineJoin='round';
  redraw();
}

function drawStroke(s){
  ctx.save();
  ctx.globalCompositeOperation=s.erase?'destination-out':'source-over';
  ctx.strokeStyle=s.color;ctx.lineWidth=s.size;
  if(s.pts.length<2){
    ctx.beginPath();ctx.arc(s.pts[0].x,s.pts[0].y,s.size/2,0,Math.PI*2);
    ctx.fillStyle=s.color;ctx.fill();
  }else{
    ctx.beginPath();ctx.moveTo(s.pts[0].x,s.pts[0].y);
    for(let i=1;i<s.pts.length;i++)ctx.lineTo(s.pts[i].x,s.pts[i].y);
    ctx.stroke();
  }
  ctx.restore();
}
function redraw(){
  ctx.clearRect(0,0,cv.width,cv.height);
  for(const s of strokes)drawStroke(s);
}

// ── tool UI
function setTool(t){
  tool=t;
  $('wb-pen').classList.toggle('on',t==='pen');
  $('wb-erase').classList.toggle('on',t==='erase');
  cv.style.cursor=t==='erase'?'cell':'crosshair';
}
$('wb-pen').onclick=()=>setTool('pen');
$('wb-erase').onclick=()=>setTool('erase');
$('wb-color').oninput=e=>color=e.target.value;
$('wb-size').oninput=e=>{size=parseInt(e.target.value,10);$('wb-size-v').textContent=size};
$('wb-clear').onclick=()=>{
  strokes=[];redraw();
  updateCounts();
  bcast(JSON.stringify({t:'wb',kind:'clear',id:myId}));
};
$('jBtn').onclick=()=>{
  const r=$('rIn').value.trim()||'acg-whiteboard';
  location.hash='room='+encodeURIComponent(r);
  join(r);
};

// ── pointer → stroke
let cur=null;
function pt(e){
  const r=cv.getBoundingClientRect();
  return{x:e.clientX-r.left,y:e.clientY-r.top};
}
cv.addEventListener('pointerdown',e=>{
  cv.setPointerCapture(e.pointerId);
  cur={id:myId+':'+Date.now()+':'+Math.random().toString(36).slice(2,6),
       color,size,erase:tool==='erase',pts:[pt(e)]};
  strokes.push(cur);drawStroke(cur);
});
cv.addEventListener('pointermove',e=>{
  if(!cur||!e.buttons)return;
  cur.pts.push(pt(e));drawStroke(cur);
});
function endStroke(){
  if(!cur)return;
  bcast(JSON.stringify({t:'wb',kind:'stroke',stroke:cur,from:myId}));
  updateCounts();cur=null;
}
cv.addEventListener('pointerup',endStroke);
cv.addEventListener('pointercancel',endStroke);
cv.addEventListener('pointerleave',endStroke);

// ── incoming strokes from peers
registerPeerHandler('wb',(m,rid)=>{
  if(m.kind==='stroke'&&m.stroke){
    strokes.push(m.stroke);drawStroke(m.stroke);updateCounts();
  }else if(m.kind==='clear'){
    strokes=[];redraw();updateCounts();
  }
});

// ── stats
function updateCounts(){
  $('wb-n').textContent=strokes.length;
  $('wb-peers').textContent=pm.size;
}
setInterval(updateCounts,1500);

// ── go
window.addEventListener('resize',fitCanvas);
fitCanvas();
log('⚒ ACG P2P Whiteboard','hi');
log('peer: '+myId+' (20 bytes ✓)','hi');

startErrorCapture();
startAuth();
setTimeout(()=>join(roomName),300);
setInterval(()=>{if(wsReady())announce()},30000);
