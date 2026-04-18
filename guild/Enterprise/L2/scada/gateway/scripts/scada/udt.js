// ═══ UDT · User Defined Types ═══
// Schemas for structured tag payloads. mkUDT(type,data) returns a normalized
// object with every declared field present (unset → null) so the monitor/HMI
// can render consistent columns.

export const UDT={
  Peer:{fields:['id','name','emoji','avatar','state','channels','connectedAt','msgsIn','msgsOut','lastSeen']},
  Tracker:{fields:['url','state','connectedAt','announces','lastAnnounceAt','connectedCount','configuredCount']},
  TrackerEndpoint:{fields:['url','state','rttMs','lastAt']},
  Room:{fields:['name','hash','peerCount','joinedAt']},
  Channel:{fields:['id','peerId','state','openedAt']},
  Profile:{fields:['provider','id','username','avatar']},
  SignalEvent:{fields:['kind','dir','peerId','offerId','ts']},
};

export function mkUDT(type,data={}){
  const def=UDT[type];
  if(!def){
    // DON'T throw — a missing UDT declaration used to take out entire
    // subsystem runtimes (e.g. p2p.js publishTrackers() threw before
    // its WebSocket handlers were attached, leaving every tracker
    // silently headless). Degrade: warn, stash every data key on a
    // best-effort object, keep the plant alive.
    try{console.warn('mkUDT: unknown UDT '+type+' — degrade to passthrough')}catch(e){}
    return{_udt:type,...(data||{})};
  }
  const o={_udt:type};
  for(const f of def.fields)o[f]=data[f]??null;
  return o;
}
