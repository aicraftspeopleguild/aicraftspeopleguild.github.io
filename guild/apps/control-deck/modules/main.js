// ═══ main · boot sequence for the control deck ═══
import { bootAuth }               from './auth.js';
import { bootActions, bootWriteForm } from './cmd.js';
import { bootPreview }            from './preview.js';
import { bootAutofire, renderBackChip } from './autofire.js';
import { log }                    from './log.js';

bootAuth();
bootActions();
bootWriteForm();
bootPreview();
renderBackChip();
bootAutofire();
window.addEventListener('hashchange', bootAutofire);

log('control deck ready', 'ok');
