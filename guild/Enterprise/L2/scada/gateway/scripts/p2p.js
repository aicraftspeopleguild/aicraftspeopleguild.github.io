import {log,badge} from './ui.js';
import {TRACKERS,ICE,N_OFFERS,myId} from './config.js';
import {pm,wire,updPeers} from './peers.js';
import {addMsg} from './chat.js';
import {ROOM,TRACKER,SIGNAL,PEERS} from './scada/providers.js';
import {mkUDT} from './scada/udt.js';

// ═══ Multi-tracker signalling ════════════════════════════════════════
// We dial every tracker in TRACKERS simultaneously so peers on different
// trackers still find each other. Each tracker gets its OWN fresh batch
// of offers (unique offer_ids) so two peers on different trackers can
// answer distinct offers without colliding on a shared id.
//
// With N_OFFERS=5 and 3 trackers, the initial pool is ≤15 PCs and a
// 30 s re-announce + 60 s TTL caps the steady-state pool ≤ 30 PCs,
// safely under Chrome's ~500 cap.

let hash=null,room='',reTimer=null;
const sockets=new Map();             // url -> WebSocket
const reconnectTimers=new Map();     // url -> setTimeout handle
const reconnectAttempts=new Map();   // url -> count (for back-off)
const pending=new Map();             // offer_id -> RTCPeerConnection

const PENDING_TTL_MS=60000;
// Some public trackers (webtorrent.dev behind Cloudflare) routinely
// take 5-10 s for the WSS handshake on a cold connection even when
// they're healthy. Keep this generous so we don't flap.
const CONNECT_TIMEOUT_MS=10000;
const RECONNECT_BACKOFF_MS=[3000,6000,12000,30000,60000];
// Stop retrying a URL after this many failed attempts in a row — keeps
// the log readable when a tracker is permanently offline.
const RECONNECT_GIVE_UP_AT=8;

// ── utility ─────────────────────────────────────────────────────────
async function mkHash(name){
  const buf=await crypto.subtle.digest('SHA-1',new TextEncoder().encode('acg:'+name));
  return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,'0')).join('');
}
function urlIdx(url){return TRACKERS.indexOf(url)}
function openSockets(){const out=[];for(const[,s]of sockets)if(s.readyState===1)out.push(s);return out}
function openUrls(){const out=[];for(const[u,s]of sockets)if(s.readyState===1)out.push(u);return out}

// ── tag plant reflect ───────────────────────────────────────────────
function publishTrackers(){
  for(const url of TRACKERS){
    const s=sockets.get(url);
    const state = !s                ? 'offline'
                : s.readyState===0  ? 'connecting'
                : s.readyState===1  ? 'connected'
                : 'offline';
    TRACKER.write('trackers.'+urlIdx(url),mkUDT('TrackerEndpoint',{
      url,state,rttMs:null,lastAt:Date.now(),
    }));
  }
  const opens=openUrls();
  const overallState = opens.length ? 'connected'
                     : [...sockets.values()].some(s=>s.readyState===0) ? 'connecting'
                     : reconnectTimers.size ? 'reconnecting'
                     : 'offline';
  const primary = opens[0] || '';
  TRACKER.write('current',mkUDT('Tracker',{
    url:primary, state:overallState,
    connectedAt:primary?(TRACKER.read('current')?.value?.connectedAt||Date.now()):null,
    announces:TRACKER.read('announces')?.value||0,
    lastAnnounceAt:TRACKER.read('lastAnnounceAt')?.value||null,
    connectedCount:opens.length,
    configuredCount:TRACKERS.length,
  }));
  TRACKER.write('state',overallState);
  TRACKER.write('count',opens.length,{type:'Counter'});
  badge(overallState==='connected'?'connected'
       :overallState==='reconnecting'?'reconnecting'
       :overallState==='connecting'?'connecting'
       :'offline');
}

// ── ICE + offer generation ──────────────────────────────────────────
function waitIce(pc,ms=4000){
  return new Promise(r=>{
    if(pc.iceGatheringState==='complete')return r();
    const t=setTimeout(r,ms);
    pc.onicegatheringstatechange=()=>{if(pc.iceGatheringState==='complete'){clearTimeout(t);r()}};
  });
}

// Mint n offers in PARALLEL. With serial mkOffers + N_OFFERS=5 and a
// 4 s ICE timeout each, we could take 20 s to announce — past most
// WSS-tracker idle windows. Parallel gathers in ≤ 4 s total.
export async function mkOffers(n){
  const tasks=[];
  for(let i=0;i<n;i++){
    tasks.push((async()=>{
      const oid=crypto.randomUUID();
      const pc=new RTCPeerConnection(ICE);
      const dc=pc.createDataChannel('acg',{ordered:true});
      wire(dc,oid);
      const offer=await pc.createOffer();
      await pc.setLocalDescription(offer);
      await waitIce(pc);
      pending.set(oid,pc);
      setTimeout(()=>{
        if(!pending.has(oid))return;
        pending.delete(oid);
        const st=pc.connectionState;
        if(st!=='connected'&&st!=='connecting')try{pc.close()}catch(e){}
      },PENDING_TTL_MS);
      return{offer_id:oid,offer:{type:'offer',sdp:pc.localDescription.sdp}};
    })());
  }
  return Promise.all(tasks);
}

// ── offer/answer handlers ───────────────────────────────────────────
async function onOffer(msg,sock){
  const rid=msg.peer_id;
  log('← offer from '+rid.slice(-8),'hi');
  SIGNAL.write('last',mkUDT('SignalEvent',{kind:'offer',dir:'in',peerId:rid,offerId:msg.offer_id,ts:Date.now()}));
  SIGNAL.inc('offersIn');
  const pc=new RTCPeerConnection(ICE);
  pc.ondatachannel=e=>wire(e.channel,rid);
  try{
    await pc.setRemoteDescription(msg.offer);
    const ans=await pc.createAnswer();
    await pc.setLocalDescription(ans);
    await waitIce(pc);
    if(sock.readyState===1){
      sock.send(JSON.stringify({
        action:'announce',info_hash:hash,peer_id:myId,
        to_peer_id:rid,answer:{type:'answer',sdp:pc.localDescription.sdp},offer_id:msg.offer_id,
      }));
    }
    log('→ answer to '+rid.slice(-8),'ok');
    SIGNAL.write('last',mkUDT('SignalEvent',{kind:'answer',dir:'out',peerId:rid,offerId:msg.offer_id,ts:Date.now()}));
    SIGNAL.inc('answersOut');
  }catch(e){log('offer handling failed: '+e.message,'er')}
}

async function onAnswer(msg){
  const pc=pending.get(msg.offer_id);
  if(!pc)return;
  pending.delete(msg.offer_id);
  log('← answer for '+msg.offer_id.slice(0,8),'hi');
  SIGNAL.write('last',mkUDT('SignalEvent',{kind:'answer',dir:'in',offerId:msg.offer_id,ts:Date.now()}));
  SIGNAL.inc('answersIn');
  try{await pc.setRemoteDescription(msg.answer)}catch(e){log('answer err: '+e.message,'er')}
}

// ── announce (per-tracker) ──────────────────────────────────────────
// Each tracker gets its own fresh offer batch with unique offer_ids so
// peers on different trackers can answer distinct offers without
// colliding. Includes event:'started' on first announce per convention.
const startedOn=new Set(); // urls we've done the 'started' announce on

async function announceOn(sock){
  if(sock.readyState!==1)return;
  const url=[...sockets.entries()].find(([,s])=>s===sock)?.[0]||'';
  const offers=await mkOffers(N_OFFERS);
  const event=startedOn.has(url)?undefined:'started';
  if(event)startedOn.add(url);
  const payload={
    action:'announce',info_hash:hash,peer_id:myId,
    numwant:50,uploaded:0,downloaded:0,left:1,offers,
  };
  if(event)payload.event=event;
  if(sock.readyState!==1)return;
  try{sock.send(JSON.stringify(payload))}
  catch(e){log('send err '+url+': '+e.message,'er');return}
  TRACKER.inc('announces');
  TRACKER.write('lastAnnounceAt',Date.now(),{type:'DateTime'});
  log('→ announce '+N_OFFERS+' offers · '+(url.split('/')[2]||url),'hi');
}

export async function announce(){
  const opens=openSockets();
  if(!opens.length){log('announce skipped — no open trackers','wr');return}
  // fan out in parallel — each tracker gets its own fresh batch
  await Promise.all(opens.map(s=>announceOn(s).catch(e=>log('announceOn err: '+e.message,'er'))));
}

// ── per-tracker connect with exponential-backoff reconnect ──────────
export function connectTracker(url){
  const existing=sockets.get(url);
  if(existing&&(existing.readyState===0||existing.readyState===1))return;

  if(reconnectTimers.has(url)){clearTimeout(reconnectTimers.get(url));reconnectTimers.delete(url)}
  // Quiet the log after a few retries so a dead tracker doesn't spam.
  const attempts=reconnectAttempts.get(url)||0;
  const verbose=attempts<3;
  if(verbose)log('trying: '+url,'hi');
  let sock;
  try{sock=new WebSocket(url)}
  catch(e){if(verbose)log('✗ '+url+' — '+e.message,'er');scheduleReconnect(url);return}

  sockets.set(url,sock);
  // SHIELD the tag-plant reflect — if it throws we must still attach
  // sock.onopen / onmessage / onclose. A missing UDT once caused every
  // handler to be skipped; the socket would open silently and the page
  // looked like "tracker not connecting". Keep wired first, reflect second.
  try{publishTrackers()}catch(e){try{console.error('publishTrackers err',e)}catch(_){}}

  const toHandle=setTimeout(()=>{
    if(sock.readyState!==1){
      if(verbose)log('✗ '+url+' — connect timeout','er');
      try{sock.close()}catch(e){}
    }
  },CONNECT_TIMEOUT_MS);

  sock.onopen=async()=>{
    clearTimeout(toHandle);
    reconnectAttempts.set(url,0);
    log('✓ '+url,'ok');
    addMsg(null,null,null,'✓ tracker '+url.split('/')[2]+' connected',true);
    try{publishTrackers()}catch(e){try{console.error('publishTrackers err',e)}catch(_){}}
    try{await announceOn(sock)}
    catch(e){log('initial announce err '+url+': '+e.message,'er')}
  };

  sock.onmessage=async e=>{
    try{
      const m=JSON.parse(e.data);
      if(m['failure reason']){log('tracker '+url+' refused: '+m['failure reason'],'er');return}
      if(m.offer&&m.peer_id&&m.peer_id!==myId)await onOffer(m,sock);
      if(m.answer&&m.offer_id)await onAnswer(m);
      if(m.interval){
        const sec=Math.min(m.interval,30);
        if(reTimer)clearTimeout(reTimer);
        reTimer=setTimeout(announce,sec*1000);
      }
    }catch(er){log('msg err: '+er.message,'er')}
  };

  sock.onerror=()=>{/* close follows */};

  sock.onclose=()=>{
    clearTimeout(toHandle);
    sockets.delete(url);
    startedOn.delete(url);
    try{publishTrackers()}catch(e){try{console.error('publishTrackers err',e)}catch(_){}}
    if(!room)return;
    scheduleReconnect(url);
  };
}

function scheduleReconnect(url){
  const n=(reconnectAttempts.get(url)||0);
  reconnectAttempts.set(url,n+1);
  if(n>=RECONNECT_GIVE_UP_AT){
    // one final log, then stop. pm + already-open trackers keep working.
    if(n===RECONNECT_GIVE_UP_AT)log('✗ '+url+' unreachable — giving up after '+n+' attempts','er');
    return;
  }
  const ms=RECONNECT_BACKOFF_MS[Math.min(n,RECONNECT_BACKOFF_MS.length-1)];
  // log only the first few retries to keep the gateway-log readable
  if(n<3)log('↻ '+url+' in '+(ms/1000)+'s','wr');
  reconnectTimers.set(url,setTimeout(()=>connectTracker(url),ms));
}

// ── join: fan out to every tracker in parallel ──────────────────────
export async function join(rName){
  for(const[,t]of reconnectTimers)clearTimeout(t);
  reconnectTimers.clear();
  reconnectAttempts.clear();
  startedOn.clear();
  for(const[,s]of sockets){s.onclose=null;s.onerror=null;s.onmessage=null;try{s.close()}catch(e){}}
  sockets.clear();
  if(reTimer){clearTimeout(reTimer);reTimer=null}
  for(const[,pc]of pending)try{pc.close()}catch(e){}
  pending.clear();
  for(const[,info]of pm)for(const dc of info.dcs)try{dc.close()}catch(e){}
  pm.clear();PEERS.clear();updPeers();

  room=rName;hash=await mkHash(rName);
  log('room: '+rName+' hash: '+hash.slice(0,12)+'... · dialling '+TRACKERS.length+' trackers','hi');
  badge('connecting');
  ROOM.write('data',mkUDT('Room',{name:rName,hash,peerCount:1,joinedAt:Date.now()}));
  ROOM.write('name',rName);ROOM.write('hash',hash);ROOM.write('joinedAt',Date.now(),{type:'DateTime'});
  addMsg(null,null,null,'Joining '+rName+' via '+TRACKERS.length+' trackers…',true);

  for(const url of TRACKERS)connectTracker(url);
}

export function bcast(msg){
  const d=JSON.stringify(msg);let n=0;
  for(const[,info]of pm)for(const dc of info.dcs)if(dc.readyState==='open'){try{dc.send(d);n++}catch(e){}}
  return n;
}

export function wsReady(){return openSockets().length>0}
