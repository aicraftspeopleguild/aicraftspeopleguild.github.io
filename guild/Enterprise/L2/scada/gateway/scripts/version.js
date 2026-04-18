import {$} from './ui.js';
import {VERSION} from './scada/providers.js';

const REPO='teslasolar/ACGP2P';
const BRANCH='main';
const CACHE_KEY='acg.version';

// Skip the network if cache is younger than this (prevents re-fetch on
// every tab-switch).
const SOFT_TTL   = 90 * 1000;      // 1.5 min

// Flag the pill amber/red if no successful fetch within these windows.
// GitHub anonymous rate limit is 60/hr; 90 s polling = 40/hr, safe.
const STALE_MS   = 3 * 60 * 1000;  // 3 min  → amber
const ERR_MS     = 10 * 60 * 1000; // 10 min → red
const POLL_MS    = 90 * 1000;      // same as SOFT_TTL

let last=loadCache();

function loadCache(){
  try{const c=JSON.parse(localStorage.getItem(CACHE_KEY)||'null');return c&&c.sha?c:null}
  catch{return null}
}
function saveCache(rec){
  try{localStorage.setItem(CACHE_KEY,JSON.stringify(rec))}catch(e){}
}

function rel(ts){
  const s=Math.floor((Date.now()-new Date(ts).getTime())/1000);
  if(s<60)return s+'s ago';
  if(s<3600)return Math.floor(s/60)+'m ago';
  if(s<86400)return Math.floor(s/3600)+'h ago';
  return Math.floor(s/86400)+'d ago';
}

function classify(){
  if(!last)return 'error';           // no data at all
  const age=Date.now()-(last.fetchedAt||0);
  if(age>ERR_MS)return 'error';      // cache exists but is ancient
  if(age>STALE_MS)return 'stale';    // cache drifting
  if(last.rateLimited)return 'stale';
  return 'ok';
}

function paint(){
  const el=$('ver');if(!el)return;
  const state=classify();
  el.classList.remove('v-stale','v-error');
  if(state==='error')el.classList.add('v-error');
  else if(state==='stale')el.classList.add('v-stale');

  if(!last){
    el.textContent='⌖ dev';
    el.title='no commit data yet · GitHub API unreachable';
    return;
  }

  const marker = state==='ok' ? '⌖' : state==='stale' ? '⌖❗' : '⌖⚠';
  el.textContent=`${marker} ${last.sha.slice(0,7)} · ${rel(last.date)}`;
  el.href=last.url;

  const parts=[
    last.msg,
    new Date(last.date).toLocaleString(),
    `last API check: ${rel(last.fetchedAt||Date.now())}`,
  ];
  if(last.rateLimited)parts.push('⚠ GitHub API rate-limited — may be behind');
  if(state==='stale')parts.push('⚠ cache drifting (>3 min since last successful check)');
  if(state==='error')parts.push('🔴 no successful check in >10 min');
  el.title=parts.join('\n');
}

function publishTags(){
  if(!last)return;
  VERSION.write('sha',last.sha);
  VERSION.write('shortSha',last.sha.slice(0,7));
  VERSION.write('committedAt',last.date,{type:'DateTime'});
  VERSION.write('message',last.msg);
  VERSION.write('url',last.url);
  VERSION.write('rateLimited',!!last.rateLimited);
  VERSION.write('state',classify());
}

async function fetchVersion(){
  // soft TTL: skip if we JUST fetched
  if(last&&(Date.now()-(last.fetchedAt||0))<SOFT_TTL){paint();publishTags();return}
  const headers={'Accept':'application/vnd.github+json'};
  if(last?.etag)headers['If-None-Match']=last.etag;
  try{
    const r=await fetch(`https://api.github.com/repos/${REPO}/commits/${BRANCH}`,{headers});
    if(r.status===304){                       // unchanged — bump fetchedAt
      last.fetchedAt=Date.now();last.rateLimited=false;saveCache(last);
      paint();publishTags();return;
    }
    if(r.status===403){                       // rate-limited — keep cache, flag it
      if(last){last.rateLimited=true;saveCache(last)}
      paint();publishTags();return;
    }
    if(!r.ok)throw new Error('HTTP '+r.status);
    const c=await r.json();
    last={
      sha:c.sha,
      date:c.commit.author.date,
      url:c.html_url,
      msg:c.commit.message.split('\n')[0],
      etag:r.headers.get('etag')||null,
      fetchedAt:Date.now(),
      rateLimited:false,
    };
    saveCache(last);paint();publishTags();
  }catch(e){
    // network error — keep cache if we have one; classify() will flag it stale
    paint();publishTags();
    const el=$('ver');if(el)el.title=(el.title||'')+'\n' + '🔴 '+e.message;
  }
}

async function refresh(){                      // force a skip-soft-ttl fetch
  if(last)last.fetchedAt=0;
  return fetchVersion();
}

export function startVersion(){
  paint();publishTags();   // show cached immediately
  fetchVersion();
  setInterval(paint,15_000);       // re-classify + refresh "Nm ago"
  setInterval(fetchVersion,POLL_MS);

  // click-with-shift forces a refetch (bypass soft TTL); left-click keeps
  // the normal navigate-to-commit-URL behaviour.
  const el=$('ver');
  if(el)el.addEventListener('click',e=>{
    if(e.shiftKey){e.preventDefault();refresh()}
  });
}
