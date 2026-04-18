// ═══ MCP Tools Engine — re-export shim ═══
// The real implementation lives under ./mcp/ split by concern:
//
//   mcp/repo.js      shared repo state + publish()
//   mcp/vfs.js       createFile, editFile, patchFile, deleteFile, readFile,
//                    listFiles, searchFiles, getAllFiles,
//                    mkdir, mv, cp, tree
//   mcp/git.js       initRepo, commitChanges, getLog, getDiff, getStatus,
//                    checkout, branch, listBranches, getRepoState,
//                    exportRepo, importRepo
//   mcp/preview.js   getPreviewableFiles, getPreviewHTML, getPreviewBlobUrl,
//                    bundle
//   mcp/scaffold.js  scaffold, SCAFFOLD_KINDS
//   mcp/tools.js     parseToolCalls, DISPATCH, executeTool,
//                    buildToolSystemPrompt
//
// UDTs: /controls/sandbox/web-llm/udts.json
// Tags: /controls/sandbox/web-llm/tags.json

export {
  createFile, editFile, patchFile, deleteFile, readFile,
  listFiles, searchFiles, getAllFiles,
  mkdir, moveFile, copyFile, tree,
} from './mcp/vfs.js';

export {
  initRepo, commitChanges, getLog, getDiff, getStatus,
  checkout, branch, listBranches, getRepoState,
  exportRepo, importRepo,
} from './mcp/git.js';

export {
  getPreviewableFiles, getPreviewHTML, getPreviewBlobUrl, bundle,
} from './mcp/preview.js';

export {scaffold, SCAFFOLD_KINDS} from './mcp/scaffold.js';

export {
  parseToolCalls, DISPATCH, executeTool, buildToolSystemPrompt,
} from './mcp/tools.js';
