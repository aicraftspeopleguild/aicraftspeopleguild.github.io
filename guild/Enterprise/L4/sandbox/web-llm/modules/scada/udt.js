// ═══ Web-LLM UDTs ═══
// Structured schemas for tag payloads published by this tool. Mirrors the
// pattern used in /controls/scada/gateway/scripts/scada/udt.js for the
// main ACG app. Declarative counterpart lives at ../../udts.json.

export const UDT={
  // runtime
  Model:    {fields:['id','size','loaded','loadedAt','progress','status']},
  Engine:   {fields:['ready','generating','streamedTokens','lastLatencyMs']},

  // voice / emotion
  Voice:    {fields:['micConnected','listening','rms','f0','energy','vowel','coherence','pulseRate']},
  Emotion:  {fields:['dominant','excitement','calm','anger','sadness','joy','curiosity']},

  // virtual filesystem
  VFile:    {fields:['path','type','size','mtime']},
  Directory:{fields:['path','entries','fileCount','mtime']},
  FileTree: {fields:['root','nodes','fileCount']},

  // git-lite
  Commit:   {fields:['id','message','ts','files']},
  Branch:   {fields:['name','head','commitCount']},
  Status:   {fields:['clean','added','modified','deleted','commits']},
  Diff:     {fields:['ref','added','modified','deleted']},

  // preview + export
  Preview:  {fields:['path','sizeBytes','inlined','ts']},
  ExportArtifact:{fields:['format','size','ts']},
  Scaffold: {fields:['kind','files','entry']},

  // chat / tools
  ToolCall: {fields:['name','args','ok','result','ts']},
  ChatMsg:  {fields:['role','len','ts','emoTag']},
};

export function mkUDT(type,data={}){
  const def=UDT[type];
  if(!def)throw new Error('unknown UDT: '+type);
  const o={_udt:type};
  for(const f of def.fields)o[f]=data[f]??null;
  return o;
}
