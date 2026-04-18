// ═══ Web-LLM config ═══
// Model catalog. Selected is the recommended default.

export const MODELS=[
  {id:'SmolLM2-135M-Instruct-q4f16_1-MLC',  label:'SmolLM2-135M — 719MB (fastest)'},
  {id:'Qwen2.5-0.5B-Instruct-q4f16_1-MLC',  label:'Qwen2.5-0.5B — 945MB'},
  {id:'Llama-3.2-1B-Instruct-q4f16_1-MLC',  label:'Llama-3.2-1B — 1.2GB (recommended)', selected:true},
  {id:'Gemma-2-2b-it-q4f16_1-MLC',          label:'Gemma-2-2B — 2.0GB'},
  {id:'Qwen2.5-1.5B-Instruct-q4f16_1-MLC',  label:'Qwen2.5-1.5B — 1.6GB'},
  {id:'Phi-3.5-mini-instruct-q4f16_1-MLC',  label:'Phi-3.5-mini — 3.6GB'},
  {id:'Llama-3.2-3B-Instruct-q4f16_1-MLC',  label:'Llama-3.2-3B — 2.9GB'},
];

export const WEBLLM_URL='https://esm.run/@mlc-ai/web-llm';

export const DEFAULT_REPO='my-project';

export const EMOTION_KEYS=['excitement','calm','anger','sadness','joy','curiosity'];
