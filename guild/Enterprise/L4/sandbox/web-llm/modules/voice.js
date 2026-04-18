// ═══ Voice capture + emotion inference ═══
// Mic → AnalyserNode → autocorrelation F0, formant vowel, onset pulse,
// simple 6-axis emotion scoring. Speech recognition runs in parallel and
// fires `onTranscript(text)` when final.

import {EMOTION_KEYS} from './config.js';
import {VOICE,EMOTION} from './scada/providers.js';
import {mkUDT} from './scada/udt.js';

export const voice={rms:0,f0:0,pDelta:0,sustain:0,coherence:0,vowel:'',pulseRate:0,energy:0};
export const emotions={excitement:0,calm:0.5,anger:0,sadness:0,joy:0,curiosity:0};
export let dominantEmo='calm';

let audioCtx=null,analyser=null,micStream=null,dataArray=null,freqArray=null;
let recognition=null,micActive=false;
let onLevel=null,onStatus=null,onTranscriptInterim=null,onTranscriptFinal=null;
let onsetCount=0,lastOnset=0,smoothRms=0;

export function isMicConnected(){return !!analyser}
export function isListening(){return micActive}

export function configure({onLevel:_l,onStatus:_s,onTranscriptInterim:_i,onTranscriptFinal:_f}={}){
  onLevel=_l;onStatus=_s;onTranscriptInterim=_i;onTranscriptFinal=_f;
}

function setStatus(t){onStatus?.(t)}

export async function setupMic(){
  try{
    setStatus('Requesting mic access...');
    micStream=await navigator.mediaDevices.getUserMedia({audio:true});
    audioCtx=new(window.AudioContext||window.webkitAudioContext)();
    if(audioCtx.state==='suspended')await audioCtx.resume();
    analyser=audioCtx.createAnalyser();
    analyser.fftSize=2048;
    analyser.smoothingTimeConstant=0.8;
    audioCtx.createMediaStreamSource(micStream).connect(analyser);
    dataArray=new Float32Array(analyser.fftSize);
    freqArray=new Uint8Array(analyser.frequencyBinCount);
    VOICE.write('micConnected',true);
    setStatus('Mic connected — click mic button for voice chat');
    requestAnimationFrame(analyzeLoop);
    return true;
  }catch(e){
    VOICE.write('micConnected',false,{quality:'bad'});
    setStatus('Mic error: '+(e.name==='NotAllowedError'?'Permission denied':e.message));
    return false;
  }
}

function analyzeLoop(){
  if(!analyser)return;
  analyser.getFloatTimeDomainData(dataArray);
  analyser.getByteFrequencyData(freqArray);

  // RMS
  let sum=0;
  for(let i=0;i<dataArray.length;i++)sum+=dataArray[i]*dataArray[i];
  const rms=Math.sqrt(sum/dataArray.length);
  smoothRms=smoothRms*0.8+rms*0.2;
  voice.rms=smoothRms;
  voice.energy=Math.min(1,smoothRms*8);

  // F0 via autocorrelation
  const sr=audioCtx.sampleRate;
  let bestCorr=0,bestLag=0;
  for(let lag=Math.floor(sr/500);lag<Math.floor(sr/60);lag++){
    let corr=0;
    for(let i=0;i<dataArray.length-lag;i++)corr+=dataArray[i]*dataArray[i+lag];
    if(corr>bestCorr){bestCorr=corr;bestLag=lag}
  }
  const f0=bestLag>0?sr/bestLag:0;
  voice.pDelta=Math.abs(f0-voice.f0);
  voice.f0=f0;
  voice.sustain=f0>60?Math.min(1,voice.sustain+0.02):voice.sustain*0.95;
  voice.coherence=bestCorr>0?Math.min(1,bestCorr/(dataArray.length*0.01)):0;

  // Onset
  if(rms>0.04&&Date.now()-lastOnset>120){onsetCount++;lastOnset=Date.now()}
  voice.pulseRate=Math.min(1,onsetCount/30);
  if(Date.now()%2000<20)onsetCount=Math.max(0,onsetCount-5);

  // Formant vowel
  let peakBin=0,peakVal=0;
  const binHz=sr/analyser.fftSize;
  for(let i=Math.floor(200/binHz);i<Math.floor(3000/binHz);i++){
    if(freqArray[i]>peakVal){peakVal=freqArray[i];peakBin=i}
  }
  const formant=peakBin*binHz;
  voice.vowel=formant<400?'oo':formant<700?'oh':formant<1200?'ah':formant<2000?'eh':'ee';

  // Emotion scoring (ballpark heuristics)
  const pitch=Math.min(1,f0/400),vol=Math.min(1,smoothRms*6),pVar=Math.min(1,voice.pDelta/60);
  const tempo=voice.pulseRate,steady=voice.coherence;
  emotions.excitement=Math.min(1,pitch*0.4+vol*0.3+pVar*0.2+tempo*0.1);
  emotions.calm      =Math.min(1,(1-vol)*0.3+steady*0.3+(1-pVar)*0.2+(1-tempo)*0.2);
  emotions.anger     =Math.min(1,vol*0.4+(1-pitch)*0.1+pVar*0.2+tempo*0.3);
  emotions.sadness   =Math.min(1,(1-vol)*0.2+(1-pitch)*0.3+(1-tempo)*0.3+(1-pVar)*0.2);
  emotions.joy       =Math.min(1,pitch*0.3+vol*0.2+pVar*0.1+steady*0.2+tempo*0.2);
  emotions.curiosity =Math.min(1,pVar*0.4+pitch*0.3+(1-vol)*0.1+steady*0.2);

  let maxE=0;
  for(const[k,v]of Object.entries(emotions))if(v>maxE){maxE=v;dominantEmo=k}

  const pct=Math.min(100,Math.round(voice.energy*100));
  onLevel?.(pct,voice.energy);

  // Publish tags (throttle: every ~250ms)
  if((Date.now()&0xff)<16){
    VOICE.write('state',mkUDT('Voice',{
      micConnected:true,listening:micActive,
      rms:+smoothRms.toFixed(4),f0:Math.round(f0),energy:+voice.energy.toFixed(3),
      vowel:voice.vowel,coherence:+voice.coherence.toFixed(3),pulseRate:+voice.pulseRate.toFixed(3),
    }));
    EMOTION.write('state',mkUDT('Emotion',{dominant:dominantEmo,...emotions}));
    EMOTION.write('dominant',dominantEmo);
  }

  requestAnimationFrame(analyzeLoop);
}

export function setupRecognition(){
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){setStatus('Speech recognition unavailable');return null}
  recognition=new SR();
  recognition.continuous=true;
  recognition.interimResults=true;
  recognition.lang='en-US';

  recognition.onresult=(e)=>{
    let final='',interim='';
    for(let i=e.resultIndex;i<e.results.length;i++){
      if(e.results[i].isFinal)final+=e.results[i][0].transcript;
      else interim+=e.results[i][0].transcript;
    }
    if(interim)onTranscriptInterim?.(interim);
    if(final.trim())onTranscriptFinal?.(final.trim());
  };
  recognition.onerror=(e)=>{
    if(e.error==='no-speech'||e.error==='aborted'){if(micActive)setStatus('Listening — speak to chat...');return}
    micActive=false;VOICE.write('listening',false);
    setStatus('Voice error: '+e.error);
  };
  recognition.onend=()=>{
    if(micActive)setTimeout(()=>{try{recognition.start()}catch(e){}},150);
  };
  return recognition;
}

export async function toggleListening(){
  if(audioCtx&&audioCtx.state==='suspended')await audioCtx.resume();
  if(!analyser)await setupMic();
  if(!recognition)setupRecognition();
  if(!recognition){setStatus('Speech recognition not supported');return false}
  micActive=!micActive;
  VOICE.write('listening',micActive);
  if(micActive){try{recognition.start()}catch(e){}setStatus('Listening — speak to chat...')}
  else{recognition.stop();setStatus('Mic connected — click mic button for voice chat')}
  return micActive;
}

export async function startListeningAuto(){
  if(!analyser||!recognition)return false;
  micActive=true;
  VOICE.write('listening',true);
  try{recognition.start()}catch(e){}
  setStatus('Listening — speak to chat...');
  return true;
}

export function emotionSnapshot(){
  return{dominant:dominantEmo,values:{...emotions}};
}
