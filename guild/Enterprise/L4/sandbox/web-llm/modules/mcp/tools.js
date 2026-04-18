// ═══ MCP · fenced-block tool parser + dispatch ═══
// LLM emits fenced blocks; parseToolCalls() turns text into an ordered
// list of {name,args}; executeTool() runs one and publishes a
// tool_call envelope.
//
// The available tool set is the union of vfs.js, git.js, preview.js,
// and scaffold.js exports — every one shows up in
// buildToolSystemPrompt() so the model knows its grammar.

import {publish} from './repo.js';
import {
  createFile,editFile,patchFile,deleteFile,readFile,
  listFiles,searchFiles,mkdir,moveFile,copyFile,tree,
} from './vfs.js';
import {
  commitChanges,getLog,getDiff,getStatus,checkout,branch,
  initRepo,exportRepo,importRepo,
} from './git.js';
import {getPreviewHTML,bundle} from './preview.js';
import {scaffold,SCAFFOLD_KINDS} from './scaffold.js';

/* ═══ Fenced tool-call grammar ═══
 * Every call is one triple-backtick fence whose first line is
 *   ```<tool> <firstLineArg>
 * ...followed by optional body content (file content, patch, …).
 *
 *   create /path/file.ext       body → file content
 *   edit   /path/file.ext       body → file content
 *   patch  /path/file.ext       body → oldStr\n---\nnewStr
 *   delete /path/file.ext
 *   read   /path/file.ext
 *   list   [/prefix]
 *   search <query>
 *   mkdir  /path
 *   mv     /a   /b              (first-line:  "/a /b")
 *   cp     /a   /b
 *   tree   [/prefix]
 *   commit <message>
 *   status
 *   diff   [ref]
 *   log    [n]
 *   branch <name>
 *   checkout <ref>
 *   preview /path/file.html
 *   bundle  /path/file.html
 *   scaffold <vanilla|spa|markdown|canvas>
 *   export
 *   import                      body → JSON snapshot
 */

export function parseToolCalls(text){
  const calls=[];
  const re=/```(\w+)\s*([^\n]*)\n([\s\S]*?)```/g;
  let m;
  while((m=re.exec(text))!==null){
    const name=m[1].toLowerCase();
    const firstLine=(m[2]||'').trim();
    const body=m[3]||'';

    switch(name){
      case 'create':
      case 'edit':
        calls.push({name:name+'_file',args:{path:firstLine,content:body.replace(/\n$/,'')}});break;
      case 'patch':{
        const parts=body.split(/\n---\n/);
        if(parts.length===2)
          calls.push({name:'patch_file',args:{path:firstLine,oldStr:parts[0],newStr:parts[1].replace(/\n$/,'')}});
        break;
      }
      case 'delete': calls.push({name:'delete_file',args:{path:firstLine}});break;
      case 'read':   calls.push({name:'read_file',  args:{path:firstLine}});break;
      case 'list':   calls.push({name:'list_files', args:{prefix:firstLine||'/'}});break;
      case 'search': calls.push({name:'search_files',args:{query:(firstLine+' '+body).trim()}});break;

      case 'mkdir':  calls.push({name:'mkdir',      args:{path:firstLine}});break;
      case 'mv':
      case 'rename':{
        const parts=firstLine.split(/\s+/);
        if(parts.length>=2)calls.push({name:'mv',args:{from:parts[0],to:parts[1]}});
        break;
      }
      case 'cp':
      case 'copy':{
        const parts=firstLine.split(/\s+/);
        if(parts.length>=2)calls.push({name:'cp',args:{from:parts[0],to:parts[1]}});
        break;
      }
      case 'tree':   calls.push({name:'tree',       args:{prefix:firstLine||'/'}});break;

      case 'commit': calls.push({name:'commit',     args:{message:(firstLine+(body?' '+body:'')).trim()||'update'}});break;
      case 'status': calls.push({name:'status',     args:{}});break;
      case 'diff':   calls.push({name:'diff',       args:{ref:firstLine||undefined}});break;
      case 'log':    calls.push({name:'log',        args:{n:parseInt(firstLine,10)||20}});break;
      case 'branch': calls.push({name:'branch',     args:{name:firstLine}});break;
      case 'checkout':calls.push({name:'checkout',  args:{ref:firstLine}});break;

      case 'preview':calls.push({name:'preview',    args:{path:firstLine}});break;
      case 'bundle': calls.push({name:'bundle',     args:{path:firstLine}});break;

      case 'scaffold':calls.push({name:'scaffold',  args:{kind:firstLine||'vanilla'}});break;
      case 'export': calls.push({name:'export',     args:{}});break;
      case 'import': calls.push({name:'import',     args:{json:body}});break;
    }
  }
  return calls;
}

export const DISPATCH={
  create_file: a => createFile(a.path,a.content??''),
  edit_file:   a => editFile(a.path,a.content??''),
  patch_file:  a => patchFile(a.path,a.oldStr,a.newStr),
  delete_file: a => deleteFile(a.path),
  read_file:   a => readFile(a.path),
  list_files:  a => listFiles(a.prefix||'/'),
  search_files:a => searchFiles(a.query),

  mkdir:       a => mkdir(a.path),
  mv:          a => moveFile(a.from,a.to),
  cp:          a => copyFile(a.from,a.to),
  tree:        a => tree(a.prefix||'/'),

  commit:      a => commitChanges(a.message||'update'),
  status:      () => getStatus(),
  diff:        a => getDiff(a.ref),
  log:         a => getLog(a.n||20),
  branch:      a => branch(a.name),
  checkout:    a => checkout(a.ref),

  preview:     a => getPreviewHTML(a.path),
  bundle:      a => bundle(a.path),

  scaffold:    a => scaffold(a.kind||'vanilla'),
  export:      () => exportRepo(),
  import:      a => importRepo(a.json),
};

export function executeTool(name,args={}){
  const fn=DISPATCH[name];
  if(!fn)return{ok:false,error:'unknown tool: '+name};
  try{
    const result=fn(args);
    publish('tool_call',{name,args,ok:!!result.ok});
    return result;
  }catch(e){
    publish('tool_call',{name,args,ok:false,error:e.message});
    return{ok:false,error:e.message};
  }
}

// Re-init helper for main.js bootstrap (wraps git.initRepo with no extra ceremony).
export function initialiseRepo(name){return initRepo(name)}

export function buildToolSystemPrompt(){
  const kinds=SCAFFOLD_KINDS.join('|');
  return `You are a coding agent inside a browser sandbox with a virtual
filesystem, git-lite, and a live preview iframe. You can call tools by
emitting fenced code blocks. One tool per fence. Always use absolute
paths starting with /.

═══ FILESYSTEM ═══

\`\`\`create /path/file.ext
<file content>
\`\`\`

\`\`\`edit /path/file.ext
<new full content>
\`\`\`

\`\`\`patch /path/file.ext
<oldStr>
---
<newStr>
\`\`\`

\`\`\`delete /path/file.ext
\`\`\`

\`\`\`read /path/file.ext
\`\`\`

\`\`\`list /prefix
\`\`\`

\`\`\`search <query>
\`\`\`

\`\`\`mkdir /path
\`\`\`

\`\`\`mv /from/path /to/path
\`\`\`

\`\`\`cp /from/path /to/path
\`\`\`

\`\`\`tree /prefix
\`\`\`

═══ GIT-LITE ═══

\`\`\`commit <message>
\`\`\`

\`\`\`status
\`\`\`

\`\`\`diff [ref]
\`\`\`

\`\`\`log [n]
\`\`\`

\`\`\`branch <name>
\`\`\`

\`\`\`checkout <commit-id>
\`\`\`

═══ PREVIEW ═══

\`\`\`preview /path/file.html
\`\`\`

\`\`\`bundle /path/file.html
\`\`\`

═══ SCAFFOLDS + EXPORT ═══

\`\`\`scaffold <${kinds}>
\`\`\`

\`\`\`export
\`\`\`

\`\`\`import
<JSON repo snapshot>
\`\`\`

Rules:
- Always use absolute paths starting with /.
- After a runnable HTML file exists, emit a \`preview\` tool.
- Explain what you're doing in plain text between fences.
- Keep files small and self-contained; inline CSS/JS into HTML when that simplifies things.
- Use \`scaffold\` to bootstrap a starter, then iterate with \`edit\` / \`patch\`.
`;
}
