// ── NESW dock shell + north / west / east / south painters ────────────

import {el,esc}      from './dom.js';
import {SUBSYSTEMS,SHELL_LINKS} from './constants.js';
import {bridge}      from '../L4/sandbox/shared/mesh-bridge.js';

// ── Dock shell ────────────────────────────────────────────────────────
export function buildDockShell(root){
  root.innerHTML='';
  root.className='dock-shell';
  const docks={
    n: el('header', {class:'dock-n'}),
    w: el('aside',  {class:'dock-w'}),
    m: el('section',{class:'dock-m'}),
    e: el('aside',  {class:'dock-e'}),
    s: el('footer', {class:'dock-s'}),
  };
  root.append(docks.n,docks.w,docks.m,docks.e,docks.s);
  return docks;
}

// ── North ─────────────────────────────────────────────────────────────
export function paintNorth(host,{glyph,name,basePath}){
  host.append(el('div',{class:'dock-n-logo'},[glyph+' '+name, el('span',{},' · ACG subsystem')]));
  const shell=el('nav',{class:'dock-n-shell'},
    SHELL_LINKS.map(l=>el('a',{href:basePath+l.href},l.label))
  );
  host.append(shell);
}

// ── West: subsystem nav with collapsible children ─────────────────────
// Each SUBSYSTEMS entry renders as either:
//   - flat <a> row (no children), or
//   - <details> dropdown whose <summary> is the parent label and whose
//     body lists the children (one <a> each, visually indented).
// The current subsystem is marked `.on`; if the current subsystem is a
// child, its parent group is also opened by default.
function navAnchor({sub,glyph,name,path},{activeSub,basePath,indent}){
  return el('a',{
    class:(sub===activeSub?'on':'')+(indent?' dock-w-sub':''),
    href:basePath+path+'/',
  },[glyph+' '+name]);
}

export function paintWest(host,{sub:activeSub,basePath}){
  host.append(el('h4',{},'Subsystems'));
  const nav=el('nav',{class:'dock-w-nav'});

  for(const s of SUBSYSTEMS){
    if(!s.children||!s.children.length){
      nav.append(navAnchor(s,{activeSub,basePath,indent:false}));
      continue;
    }
    const childActive=s.children.some(c=>c.sub===activeSub);
    const parentActive=s.sub===activeSub;
    const open=childActive||parentActive;

    const details=el('details',{class:'dock-w-group'+(open?' open':'')});
    if(open)details.setAttribute('open','');

    const summary=el('summary',{class:'dock-w-summary'+(parentActive?' on':'')},
      [s.glyph+' '+s.name]
    );
    details.append(summary);

    const parentLink=el('a',{
      class:'dock-w-parent-link'+(parentActive?' on':''),
      href:basePath+s.path+'/',
    },['open '+s.name+' overview']);
    const kids=el('div',{class:'dock-w-subs'});
    kids.append(parentLink);
    for(const c of s.children){
      kids.append(navAnchor(c,{activeSub,basePath,indent:true}));
    }
    details.append(kids);
    nav.append(details);
  }
  host.append(nav);

  host.append(el('hr',{class:'dock-sep'}));
  host.append(el('h4',{},'Controls'));
  host.append(el('div',{class:'dock-w-actions'},[
    el('a',{href:basePath+'.github/ISSUE_TEMPLATE/tag-update.yml'},    '🏷️ write tag'),
    el('a',{href:basePath+'.github/ISSUE_TEMPLATE/log-entry.yml'},     '⚠ log incident'),
    el('a',{href:basePath+'.github/ISSUE_TEMPLATE/control-action.yml'},'🎛 control action'),
  ]));
}

// ── East: live clients + broadcast ───────────────────────────────────
export function paintEast(host,{sub}){
  const clientsSec=el('section',{class:'dock-e-sec'},[
    el('h3',{},'💓 Live clients'),
    el('div',{id:'dock-e-clients',class:'ix-hbrow'}),
  ]);
  host.append(clientsSec);

  const castSec=el('section',{class:'dock-e-sec'},[el('h3',{},'📣 Broadcast')]);
  const row=el('div',{class:'ix-row'});
  const input=el('input',{class:'ix-in',placeholder:'ping sibling tabs…'});
  const btn=el('button',{class:'ix-btn'},'send');
  btn.addEventListener('click',()=>{
    const v=input.value.trim()||'ping';
    bridge.publish(sub,'ping',{path:'broadcast',value:v});
    input.value='';
  });
  input.addEventListener('keydown',e=>{if(e.key==='Enter')btn.click()});
  row.append(input,btn);
  castSec.append(row);
  host.append(castSec);

  host.append(el('section',{class:'dock-e-sec'},[
    el('h3',{},'⏱ Cadence'),
    el('p',{class:'ix-muted'},'heartbeat 5 s · tag refresh 5 s · commit poll 90 s'),
  ]));
}

// ── South: rolling mesh feed ──────────────────────────────────────────
export function paintSouth(host){
  host.append(el('span',{class:'dock-s-mark'},'⚒ AI Craftspeople Guild · P2P'));
  host.append(el('span',{class:'dock-s-feed',id:'dock-s-feed'},'— idle —'));
  host.append(el('span',{class:'dock-s-cadence',id:'dock-s-cadence'},'💓 5s'));
}
